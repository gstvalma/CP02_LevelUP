# 🛠️ Prompt Toolkit — E-commerce

> Toolkit Python 3.10+ que aplica **4 técnicas de prompting** (Zero-Shot, Few-Shot, Chain-of-Thought, Role Prompting) a **3 tarefas de e-commerce** (Classificação, Extração, Geração) via API local do Ollama, com avaliação de acurácia, consistência, custo em tokens e sensibilidade à temperatura.

---

## 📁 Estrutura de Diretórios

```
toolkit/
├── main.py                     # Orquestrador principal
├── requirements.txt
├── .env.example                # Variáveis de ambiente (copiar para .env)
│
├── src/
│   ├── llm_client.py           # LLMClient → chamadas REST ao Ollama
│   ├── prompt_builder.py       # Construtores modulares de prompt
│   ├── techniques.py           # zero_shot, few_shot, chain_of_thought, role_prompting
│   ├── tasks.py                # Definição das 3 tarefas (instrução, contexto, formato)
│   ├── evaluator.py            # contar_tokens, medir_acuracia, medir_consistencia, testar_temperatura
│   └── report.py               # Geração de CSV (pandas) e gráficos (matplotlib)
│
├── data/
│   ├── inputs.json             # 5 entradas por tarefa
│   └── examples.json           # Exemplos few-shot por tarefa
│
├── prompts/
│   └── system_prompts.json     # 2 personas: Analista de E-commerce e Redator de Marketing
│
└── saida/                      # Gerada automaticamente ao executar
    ├── resultados.csv
    ├── metricas.csv
    ├── grafico_acuracia.png
    ├── grafico_tokens.png
    └── grafico_temperatura.png
```

---

## ✅ Pré-requisitos

| Requisito | Versão mínima | Link |
|---|---|---|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Ollama | Última estável | [ollama.com](https://ollama.com/) |
| Modelo | `gpt-oss:120b` | — |

Verifique se o Ollama está em execução e o modelo disponível:

```bash
ollama serve
ollama pull gpt-oss:120b

# Confirmar disponibilidade
curl http://localhost:11434/api/tags
```

---

## ⚙️ Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/prompt-toolkit.git
cd prompt-toolkit

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

**Dependências principais:**

```
requests>=2.31.0
tiktoken>=0.7.0
pandas>=2.2.0
matplotlib>=3.9.0
```

---

## 🔧 Configuração

Copie o arquivo de exemplo e ajuste conforme seu ambiente:

```bash
cp .env.example .env
```

Conteúdo do `.env`:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_TIMEOUT=120
```

`.env.example` (já incluído no repositório):

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:120b
OLLAMA_TIMEOUT=120
```

> **Nota:** o `LLMClient` usa `OLLAMA_HOST` e `OLLAMA_MODEL` diretamente do `CONFIG` em `main.py`. Para leitura automática do `.env`, adicione `python-dotenv` e chame `load_dotenv()` no topo de `main.py`.

---

## ▶️ Execução

```bash
python main.py
```

O fluxo executado:

1. Carrega tarefas (`src/tasks.py`), entradas (`data/inputs.json`), exemplos e personas.
2. Itera **3 tarefas × 5 entradas × 4 técnicas** → chama o Ollama para cada combinação.
3. Avalia acurácia (tarefas com gabarito) e mede tokens via `tiktoken`.
4. Testa consistência com 3 repetições de um prompt fixo.
5. Executa varredura de temperatura (0.1 / 0.5 / 1.0).
6. Salva todos os artefatos na pasta `saida/`.

**Saída esperada no terminal:**

```
🚀 Iniciando Toolkit de Prompting — Domínio E-commerce
   Modelo: gpt-oss:120b | Temperatura: 0.7

▶ Tarefa: Classificação de Sentimento
  ├─ Técnica: zero_shot ..... (5 execuções)
  ├─ Técnica: few_shot ..... (5 execuções)
  ...

📁 Gerando relatórios...
[Relatório] CSV salvo: saida/resultados.csv
[Relatório] Gráfico de acurácia salvo: saida/grafico_acuracia.png
...

✅ Concluído. Total de requisições: 62 | Total de tokens: 48320 | Tempo médio: 1.84s
```
