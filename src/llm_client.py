"""Cliente LLM para API local Ollama."""
import time
import requests


MODELO_PADRAO = "gpt-oss:120b"
URL_OLLAMA = "http://localhost:11434/api/chat"


class LLMClient:
    def __init__(self, modelo: str = MODELO_PADRAO, temperatura: float = 0.7, timeout: int = 120):
        self.modelo = modelo
        self.temperatura = temperatura
        self.timeout = timeout
        self.historico_requisicoes: list[dict] = []

    def _montar_mensagens(self, prompt: str, sistema: str | None = None) -> list[dict]:
        msgs = []
        if sistema:
            msgs.append({"role": "system", "content": sistema})
        msgs.append({"role": "user", "content": prompt})
        return msgs

    def completar(self, prompt: str, sistema: str | None = None, temperatura: float | None = None) -> dict:
        """Envia prompt para Ollama e retorna resposta, tokens e tempo."""
        temp = temperatura if temperatura is not None else self.temperatura
        payload = {
            "model": self.modelo,
            "messages": self._montar_mensagens(prompt, sistema),
            "options": {"temperature": temp},
            "stream": False,
        }
        inicio = time.perf_counter()
        try:
            resp = requests.post(URL_OLLAMA, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            dados = resp.json()
        except requests.exceptions.ConnectionError:
            return self._erro("Ollama não encontrado. Certifique-se que o servidor está rodando.")
        except requests.exceptions.Timeout:
            return self._erro(f"Timeout após {self.timeout}s.")
        except Exception as exc:
            return self._erro(str(exc))

        duracao = round(time.perf_counter() - inicio, 3)
        tokens_prompt = dados.get("prompt_eval_count", 0)
        tokens_resposta = dados.get("eval_count", 0)
        conteudo = dados.get("message", {}).get("content", "")

        resultado = {
            "resposta": conteudo,
            "tokens_prompt": tokens_prompt,
            "tokens_resposta": tokens_resposta,
            "tokens_total": tokens_prompt + tokens_resposta,
            "tempo_segundos": duracao,
            "modelo": self.modelo,
            "temperatura": temp,
            "sucesso": True,
        }
        self.historico_requisicoes.append(resultado)
        return resultado

    @staticmethod
    def _erro(msg: str) -> dict:
        return {
            "resposta": f"[ERRO] {msg}",
            "tokens_prompt": 0,
            "tokens_resposta": 0,
            "tokens_total": 0,
            "tempo_segundos": 0.0,
            "modelo": MODELO_PADRAO,
            "temperatura": 0.0,
            "sucesso": False,
        }

    def estatisticas(self) -> dict:
        reqs = self.historico_requisicoes
        if not reqs:
            return {}
        return {
            "total_requisicoes": len(reqs),
            "total_tokens": sum(r["tokens_total"] for r in reqs),
            "tempo_medio_s": round(sum(r["tempo_segundos"] for r in reqs) / len(reqs), 3),
        }
