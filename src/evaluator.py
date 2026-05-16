"""Funções de avaliação: tokens, acurácia, consistência e temperatura."""
import json
import re
import statistics
from src.llm_client import LLMClient

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    _ENCODER = None


def contar_tokens(texto: str) -> int:
    """Conta tokens via tiktoken (fallback: estimativa por palavras)."""
    if _ENCODER:
        return len(_ENCODER.encode(texto))
    return max(1, len(texto.split()) * 4 // 3)


def _extrair_rotulo(resposta: str, rotulos_validos: list[str]) -> str | None:
    """Extrai o rótulo da resposta tentando JSON e depois regex."""
    try:
        dados = json.loads(resposta)
        for campo in ("sentimento", "intencao"):
            if campo in dados:
                return str(dados[campo]).upper()
    except (json.JSONDecodeError, TypeError):
        pass
    for rotulo in rotulos_validos:
        if rotulo.upper() in resposta.upper():
            return rotulo.upper()
    return None


def medir_acuracia(resultados: list[dict], gabaritos: list[str], rotulos_validos: list[str]) -> dict:
    """Calcula acurácia comparando respostas com gabaritos."""
    acertos = 0
    detalhes = []
    for res, gabarito in zip(resultados, gabaritos):
        predito = _extrair_rotulo(res.get("resposta", ""), rotulos_validos)
        correto = predito == gabarito.upper() if predito else False
        acertos += int(correto)
        detalhes.append({
            "predito": predito,
            "esperado": gabarito.upper(),
            "correto": correto,
            "tecnica": res.get("tecnica", ""),
        })
    total = len(gabaritos) or 1
    return {
        "acuracia": round(acertos / total, 4),
        "acertos": acertos,
        "total": total,
        "detalhes": detalhes,
    }


def medir_consistencia(cliente: LLMClient, prompt: str, sistema: str | None = None,
                        n_repeticoes: int = 3) -> dict:
    """Mede consistência executando o mesmo prompt N vezes e comparando respostas."""
    respostas = [cliente.completar(prompt, sistema)["resposta"] for _ in range(n_repeticoes)]
    tokens_lista = [contar_tokens(r) for r in respostas]
    media_tokens = statistics.mean(tokens_lista)
    desvio_tokens = statistics.stdev(tokens_lista) if len(tokens_lista) > 1 else 0.0

    # Similaridade simples: proporção de palavras em comum com a resposta-base
    palavras_base = set(re.findall(r"\w+", respostas[0].lower()))
    similaridades = []
    for r in respostas[1:]:
        palavras_r = set(re.findall(r"\w+", r.lower()))
        uniao = palavras_base | palavras_r
        intersecao = palavras_base & palavras_r
        similaridades.append(len(intersecao) / len(uniao) if uniao else 0.0)

    return {
        "repeticoes": n_repeticoes,
        "media_tokens_resposta": round(media_tokens, 1),
        "desvio_tokens": round(desvio_tokens, 1),
        "similaridade_media": round(statistics.mean(similaridades) if similaridades else 1.0, 4),
        "respostas": respostas,
    }


def testar_temperatura(cliente: LLMClient, prompt: str, sistema: str | None = None) -> list[dict]:
    """Executa o prompt com temperaturas 0.1, 0.5 e 1.0 e retorna resultados comparativos."""
    temperaturas = [0.1, 0.5, 1.0]
    resultados = []
    for temp in temperaturas:
        res = cliente.completar(prompt, sistema, temperatura=temp)
        resultados.append({
            "temperatura": temp,
            "resposta": res["resposta"],
            "tokens_total": res["tokens_total"],
            "tempo_segundos": res["tempo_segundos"],
            "tokens_resposta": res["tokens_resposta"],
            "sucesso": res["sucesso"],
        })
    return resultados
