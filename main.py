"""
Toolkit de Técnicas de Prompting para E-commerce
Ponto de entrada: carrega config, executa técnicas, avalia e gera relatório.
"""
import json
import sys
from pathlib import Path

from src.llm_client import LLMClient
from src.tasks import TAREFAS
from src.techniques import zero_shot, few_shot, chain_of_thought, role_prompting
from src.evaluator import contar_tokens, medir_acuracia, medir_consistencia, testar_temperatura
from src.report import (
    salvar_resultados_csv, salvar_metricas_csv,
    grafico_acuracia, grafico_custo_tokens, grafico_temperatura,
    imprimir_resumo,
)

# ── Configuração ──────────────────────────────────────────────────────────────
CONFIG = {
    "modelo": "gpt-oss:120b",
    "temperatura_padrao": 0.7,
    "timeout": 120,
    "n_consistencia": 3,
    "tarefas_ativas": ["classificacao", "extracao", "geracao"],
    "tecnicas_ativas": ["zero_shot", "few_shot", "chain_of_thought", "role_prompting"],
}

# Gabaritos para avaliação de acurácia (classificação e extração)
GABARITOS: dict[str, list[str]] = {
    "classificacao": ["NEGATIVO", "POSITIVO", "NEUTRO", "NEGATIVO", "NEUTRO"],
    "extracao": ["devolucao", "rastreamento", "nota_fiscal", "cancelamento", "rastreamento"],
}


def _carregar_json(caminho: str) -> dict | list:
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _persona_para_tarefa(personas: dict, tarefa_nome: str) -> dict:
    if "geracao" in tarefa_nome:
        return personas["redator_marketing"]
    return personas["analista_ecommerce"]


def executar_tecnica(nome: str, cliente: LLMClient, tarefa: dict, entrada,
                     exemplos: list, persona: dict) -> dict | None:
    mapa = {
        "zero_shot": lambda: zero_shot(cliente, tarefa, entrada),
        "few_shot": lambda: few_shot(cliente, tarefa, entrada, exemplos),
        "chain_of_thought": lambda: chain_of_thought(cliente, tarefa, entrada),
        "role_prompting": lambda: role_prompting(cliente, tarefa, entrada, persona),
    }
    fn = mapa.get(nome)
    return fn() if fn else None


def main():
    print("\n🚀 Iniciando Toolkit de Prompting — Domínio E-commerce")
    print(f"   Modelo: {CONFIG['modelo']} | Temperatura: {CONFIG['temperatura_padrao']}\n")

    # ── Carregamento de dados ─────────────────────────────────────────────────
    entradas_por_tarefa: dict = _carregar_json("data/inputs.json")
    exemplos_por_tarefa: dict = _carregar_json("data/examples.json")
    personas: dict = _carregar_json("prompts/system_prompts.json")

    cliente = LLMClient(
        modelo=CONFIG["modelo"],
        temperatura=CONFIG["temperatura_padrao"],
        timeout=CONFIG["timeout"],
    )

    todos_resultados: list[dict] = []
    metricas_acuracia: dict[str, dict] = {}

    # ── Loop principal: tarefas × técnicas × entradas ────────────────────────
    for nome_tarefa in CONFIG["tarefas_ativas"]:
        tarefa = TAREFAS[nome_tarefa]
        entradas = entradas_por_tarefa.get(nome_tarefa, [])
        exemplos = exemplos_por_tarefa.get(nome_tarefa, [])
        persona = _persona_para_tarefa(personas, nome_tarefa)
        gabaritos = GABARITOS.get(nome_tarefa, [])

        print(f"▶ Tarefa: {tarefa['nome']}")

        for nome_tecnica in CONFIG["tecnicas_ativas"]:
            resultados_tecnica: list[dict] = []
            print(f"  ├─ Técnica: {nome_tecnica}", end="", flush=True)

            for item in entradas:
                # Monta entrada: texto para classificação/extração, dict para geração
                entrada = item.get("texto", item)
                resultado = executar_tecnica(nome_tecnica, cliente, tarefa, entrada, exemplos, persona)
                if resultado:
                    resultado["tarefa"] = nome_tarefa
                    resultado["tokens_prompt_tiktoken"] = contar_tokens(resultado.get("prompt", ""))
                    todos_resultados.append(resultado)
                    resultados_tecnica.append(resultado)
                    print(".", end="", flush=True)

            print(f" ({len(resultados_tecnica)} execuções)")

            # Acurácia apenas para tarefas com gabaritos
            if gabaritos and resultados_tecnica:
                chave = f"{nome_tarefa}|{nome_tecnica}"
                metricas_acuracia[chave] = medir_acuracia(
                    resultados_tecnica, gabaritos, tarefa.get("rotulos_validos", [])
                )

    # ── Análise de consistência (prompt fixo de classificação) ────────────────
    print("\n🔄 Testando consistência (classificação, zero_shot)...")
    prompt_consistencia = (
        "### Instrução\nClassifique o sentimento: POSITIVO, NEGATIVO ou NEUTRO.\n"
        "### Entrada\nO produto chegou no prazo e funciona bem, mas a embalagem veio amassada.\n"
        "### Formato de Saída Esperado\nJSON: {\"sentimento\": \"...\", \"confianca\": 0.0-1.0}"
    )
    consistencia = medir_consistencia(cliente, prompt_consistencia, n_repeticoes=CONFIG["n_consistencia"])
    print(f"   Similaridade média: {consistencia['similaridade_media']:.1%} | "
          f"Desvio tokens: {consistencia['desvio_tokens']}")

    # ── Teste de temperatura ──────────────────────────────────────────────────
    print("\n🌡️  Testando temperaturas (0.1 / 0.5 / 1.0)...")
    dados_temperatura = testar_temperatura(cliente, prompt_consistencia)
    for d in dados_temperatura:
        print(f"   T={d['temperatura']} → {d['tokens_resposta']} tokens | {d['tempo_segundos']}s")

    # ── Relatórios ────────────────────────────────────────────────────────────
    print("\n📁 Gerando relatórios...")
    salvar_resultados_csv(todos_resultados)
    salvar_metricas_csv(metricas_acuracia)
    grafico_acuracia(metricas_acuracia)
    grafico_custo_tokens(todos_resultados)
    grafico_temperatura(dados_temperatura)
    imprimir_resumo(todos_resultados, metricas_acuracia)

    estat = cliente.estatisticas()
    print(f"✅ Concluído. Total de requisições: {estat.get('total_requisicoes', 0)} | "
          f"Total de tokens: {estat.get('total_tokens', 0)} | "
          f"Tempo médio: {estat.get('tempo_medio_s', 0)}s\n")


if __name__ == "__main__":
    main()
