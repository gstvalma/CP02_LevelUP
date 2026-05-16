"""Funções para construção modular de prompts."""
import json


def _secao(titulo: str, conteudo: str) -> str:
    return f"### {titulo}\n{conteudo}\n"


def montar_instrucao(instrucao: str) -> str:
    return _secao("Instrução", instrucao)


def montar_contexto(contexto: str) -> str:
    return _secao("Contexto", contexto)


def montar_entrada(entrada: str | dict) -> str:
    texto = json.dumps(entrada, ensure_ascii=False) if isinstance(entrada, dict) else entrada
    return _secao("Entrada", texto)


def montar_formato_saida(formato: str) -> str:
    return _secao("Formato de Saída Esperado", formato)


def montar_exemplos(exemplos: list[dict], chave_entrada: str = "entrada", chave_saida: str = "saida") -> str:
    linhas = ["### Exemplos"]
    for i, ex in enumerate(exemplos, 1):
        ent = ex.get(chave_entrada, "")
        sai = ex.get(chave_saida, "")
        if isinstance(ent, dict):
            ent = json.dumps(ent, ensure_ascii=False)
        if isinstance(sai, dict):
            sai = json.dumps(sai, ensure_ascii=False)
        linhas.append(f"\n**Exemplo {i}:**\nEntrada: {ent}\nSaída: {sai}")
    return "\n".join(linhas) + "\n"


def montar_cadeia_raciocinio(passos: list[str]) -> str:
    linhas = ["### Raciocínio Passo a Passo"]
    linhas += [f"{i}. {p}" for i, p in enumerate(passos, 1)]
    return "\n".join(linhas) + "\n"


def construir_prompt(*blocos: str) -> str:
    """Concatena blocos de prompt em ordem."""
    return "\n".join(b for b in blocos if b)
