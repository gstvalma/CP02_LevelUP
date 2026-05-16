"""Geração de relatórios CSV e gráficos com pandas e matplotlib."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PASTA_SAIDA = Path("saida")


def _garantir_pasta(pasta: Path = PASTA_SAIDA) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def salvar_resultados_csv(resultados: list[dict], nome_arquivo: str = "resultados.csv") -> Path:
    """Persiste todos os resultados em CSV."""
    pasta = _garantir_pasta()
    linhas = []
    for r in resultados:
        linhas.append({
            "tarefa": r.get("tarefa", ""),
            "tecnica": r.get("tecnica", ""),
            "tokens_prompt": r.get("tokens_prompt", 0),
            "tokens_resposta": r.get("tokens_resposta", 0),
            "tokens_total": r.get("tokens_total", 0),
            "tempo_s": r.get("tempo_segundos", 0),
            "temperatura": r.get("temperatura", 0),
            "sucesso": r.get("sucesso", False),
            "resposta_resumida": str(r.get("resposta", ""))[:120],
        })
    caminho = pasta / nome_arquivo
    pd.DataFrame(linhas).to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"[Relatório] CSV salvo: {caminho}")
    return caminho


def salvar_metricas_csv(metricas: dict, nome_arquivo: str = "metricas.csv") -> Path:
    """Salva métricas de acurácia por tarefa e técnica."""
    pasta = _garantir_pasta()
    linhas = []
    for chave, valor in metricas.items():
        tarefa, tecnica = chave.split("|") if "|" in chave else (chave, "")
        linhas.append({
            "tarefa": tarefa,
            "tecnica": tecnica,
            "acuracia": valor.get("acuracia", 0),
            "acertos": valor.get("acertos", 0),
            "total": valor.get("total", 0),
        })
    caminho = pasta / nome_arquivo
    pd.DataFrame(linhas).to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"[Relatório] Métricas salvas: {caminho}")
    return caminho


def _estilo_grafico():
    plt.rcParams.update({
        "figure.facecolor": "#0f172a",
        "axes.facecolor": "#1e293b",
        "axes.edgecolor": "#475569",
        "axes.labelcolor": "#e2e8f0",
        "xtick.color": "#94a3b8",
        "ytick.color": "#94a3b8",
        "text.color": "#e2e8f0",
        "grid.color": "#334155",
        "grid.linestyle": "--",
        "grid.alpha": 0.5,
        "font.family": "DejaVu Sans",
    })


PALETA = ["#38bdf8", "#818cf8", "#34d399", "#fb923c"]


def grafico_acuracia(metricas: dict, nome_arquivo: str = "grafico_acuracia.png") -> Path:
    """Gráfico de barras agrupadas: acurácia por tarefa e técnica."""
    _estilo_grafico()
    pasta = _garantir_pasta()

    df = pd.DataFrame([
        {"tarefa": k.split("|")[0], "tecnica": k.split("|")[1], "acuracia": v.get("acuracia", 0)}
        for k, v in metricas.items() if "|" in k
    ])
    if df.empty:
        print("[Relatório] Sem dados para gráfico de acurácia.")
        return pasta / nome_arquivo

    pivot = df.pivot(index="tarefa", columns="tecnica", values="acuracia").fillna(0)
    ax = pivot.plot(kind="bar", figsize=(10, 5), color=PALETA[:len(pivot.columns)],
                    edgecolor="#0f172a", width=0.7)
    ax.set_title("Acurácia por Tarefa e Técnica", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Tarefa", labelpad=8)
    ax.set_ylabel("Acurácia", labelpad=8)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.set_ylim(0, 1.05)
    ax.legend(title="Técnica", bbox_to_anchor=(1.01, 1), loc="upper left", framealpha=0.3)
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y")
    plt.tight_layout()
    caminho = pasta / nome_arquivo
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Relatório] Gráfico de acurácia salvo: {caminho}")
    return caminho


def grafico_custo_tokens(resultados: list[dict], nome_arquivo: str = "grafico_tokens.png") -> Path:
    """Gráfico de barras empilhadas: tokens prompt vs resposta por técnica."""
    _estilo_grafico()
    pasta = _garantir_pasta()
    df = pd.DataFrame(resultados)
    if df.empty or "tecnica" not in df.columns:
        print("[Relatório] Sem dados para gráfico de tokens.")
        return pasta / nome_arquivo

    agrupado = df.groupby("tecnica")[["tokens_prompt", "tokens_resposta"]].mean().round(0)
    ax = agrupado.plot(kind="bar", stacked=True, figsize=(9, 5),
                       color=["#38bdf8", "#818cf8"], edgecolor="#0f172a", width=0.6)
    ax.set_title("Média de Tokens por Técnica", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Técnica", labelpad=8)
    ax.set_ylabel("Tokens", labelpad=8)
    ax.legend(["Prompt", "Resposta"], title="Tipo", framealpha=0.3)
    ax.tick_params(axis="x", rotation=10)
    ax.grid(axis="y")
    plt.tight_layout()
    caminho = pasta / nome_arquivo
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Relatório] Gráfico de tokens salvo: {caminho}")
    return caminho


def grafico_temperatura(dados_temperatura: list[dict], nome_arquivo: str = "grafico_temperatura.png") -> Path:
    """Linha: tokens de resposta e tempo por temperatura."""
    _estilo_grafico()
    pasta = _garantir_pasta()
    if not dados_temperatura:
        print("[Relatório] Sem dados de temperatura.")
        return pasta / nome_arquivo

    df = pd.DataFrame(dados_temperatura)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax2 = ax1.twinx()

    ax1.plot(df["temperatura"], df["tokens_resposta"], "o-", color="#38bdf8",
             linewidth=2, markersize=8, label="Tokens Resposta")
    ax2.plot(df["temperatura"], df["tempo_segundos"], "s--", color="#fb923c",
             linewidth=2, markersize=8, label="Tempo (s)")

    ax1.set_xlabel("Temperatura", labelpad=8)
    ax1.set_ylabel("Tokens de Resposta", color="#38bdf8", labelpad=8)
    ax2.set_ylabel("Tempo (segundos)", color="#fb923c", labelpad=8)
    ax1.set_title("Impacto da Temperatura na Resposta", fontsize=14, fontweight="bold", pad=12)
    ax1.set_xticks([0.1, 0.5, 1.0])
    ax1.grid(axis="y")

    linhas1, rot1 = ax1.get_legend_handles_labels()
    linhas2, rot2 = ax2.get_legend_handles_labels()
    ax1.legend(linhas1 + linhas2, rot1 + rot2, loc="upper left", framealpha=0.3)
    plt.tight_layout()
    caminho = pasta / nome_arquivo
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Relatório] Gráfico de temperatura salvo: {caminho}")
    return caminho


def imprimir_resumo(resultados: list[dict], metricas: dict) -> None:
    """Imprime resumo tabular no terminal."""
    print("\n" + "=" * 65)
    print("  RESUMO DO EXPERIMENTO — TÉCNICAS DE PROMPTING (E-COMMERCE)")
    print("=" * 65)
    df = pd.DataFrame(resultados)
    if not df.empty and "tecnica" in df.columns:
        resumo = df.groupby("tecnica").agg(
            total_execucoes=("tokens_total", "count"),
            media_tokens=("tokens_total", "mean"),
            media_tempo_s=("tempo_segundos", "mean"),
        ).round(2)
        print("\n📊 Estatísticas por Técnica:")
        print(resumo.to_string())

    if metricas:
        print("\n🎯 Acurácia por Tarefa/Técnica:")
        for chave, val in metricas.items():
            print(f"  {chave:<40} → {val.get('acuracia', 0):.1%}  ({val.get('acertos', 0)}/{val.get('total', 0)})")
    print("=" * 65 + "\n")
