"""Implementação das 4 técnicas de prompting."""
from src.prompt_builder import (
    montar_instrucao, montar_contexto, montar_entrada,
    montar_formato_saida, montar_exemplos, montar_cadeia_raciocinio,
    construir_prompt,
)
from src.llm_client import LLMClient


def zero_shot(cliente: LLMClient, tarefa: dict, entrada: str | dict, sistema: str | None = None) -> dict:
    """Prompt direto sem exemplos."""
    prompt = construir_prompt(
        montar_instrucao(tarefa["instrucao"]),
        montar_contexto(tarefa["contexto"]),
        montar_entrada(entrada),
        montar_formato_saida(tarefa["formato_saida"]),
    )
    resultado = cliente.completar(prompt, sistema)
    resultado["tecnica"] = "zero_shot"
    resultado["prompt"] = prompt
    return resultado


def few_shot(cliente: LLMClient, tarefa: dict, entrada: str | dict, exemplos: list[dict],
             sistema: str | None = None) -> dict:
    """Prompt com exemplos de entrada/saída."""
    prompt = construir_prompt(
        montar_instrucao(tarefa["instrucao"]),
        montar_contexto(tarefa["contexto"]),
        montar_exemplos(exemplos),
        montar_entrada(entrada),
        montar_formato_saida(tarefa["formato_saida"]),
    )
    resultado = cliente.completar(prompt, sistema)
    resultado["tecnica"] = "few_shot"
    resultado["prompt"] = prompt
    return resultado


def chain_of_thought(cliente: LLMClient, tarefa: dict, entrada: str | dict,
                     sistema: str | None = None) -> dict:
    """Prompt que instrui raciocínio passo a passo antes da resposta final."""
    passos_padrao = [
        "Leia atentamente a entrada fornecida.",
        "Identifique os elementos-chave relevantes para a tarefa.",
        "Aplique o critério da instrução a cada elemento identificado.",
        "Formule a resposta final no formato solicitado.",
    ]
    passos = tarefa.get("passos_raciocinio", passos_padrao)
    instrucao_cot = (
        tarefa["instrucao"]
        + "\n\nIMPORTANTE: Antes da resposta final, execute cada passo de raciocínio explicitamente."
        + " Ao final, escreva '**RESPOSTA FINAL:**' seguida da resposta no formato solicitado."
    )
    prompt = construir_prompt(
        montar_instrucao(instrucao_cot),
        montar_contexto(tarefa["contexto"]),
        montar_cadeia_raciocinio(passos),
        montar_entrada(entrada),
        montar_formato_saida(tarefa["formato_saida"]),
    )
    resultado = cliente.completar(prompt, sistema)
    resultado["tecnica"] = "chain_of_thought"
    resultado["prompt"] = prompt
    return resultado


def role_prompting(cliente: LLMClient, tarefa: dict, entrada: str | dict,
                   persona: dict, sistema: str | None = None) -> dict:
    """Prompt com atribuição explícita de papel/persona ao modelo."""
    sistema_persona = persona.get("persona", "")
    if sistema:
        sistema_persona = f"{sistema_persona}\n\n{sistema}"

    instrucao_role = (
        f"Como {persona.get('nome', 'especialista')}, com tom {persona.get('tom', 'profissional')}, "
        f"{tarefa['instrucao']}"
    )
    prompt = construir_prompt(
        montar_instrucao(instrucao_role),
        montar_contexto(tarefa["contexto"]),
        montar_entrada(entrada),
        montar_formato_saida(tarefa["formato_saida"]),
    )
    resultado = cliente.completar(prompt, sistema_persona)
    resultado["tecnica"] = "role_prompting"
    resultado["persona"] = persona.get("nome", "desconhecida")
    resultado["prompt"] = prompt
    return resultado
