import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def gerar_grafico_pizza(dados, titulo: str, caminho_arquivo="grafico_ranking.png"):
    """Recebe uma lista [(nome_adm, total), ...] e salva um gráfico de pizza em PNG."""
    nomes = [item[0] for item in dados]
    totais = [item[1] for item in dados]

    cores = [
        "#FF69B4", "#1F1F1F", "#FFB6C1", "#C71585", "#4A4A4A",
        "#FF1493", "#8B5CF6", "#F472B6", "#6B7280", "#EC4899",
        "#DB2777", "#9CA3AF"
    ]

    fig, ax = plt.subplots(figsize=(7, 5), facecolor="white")
    ax.set_facecolor("white")

    wedges, texts, autotexts = ax.pie(
        totais,
        labels=nomes,
        autopct="%1.1f%%",
        startangle=140,
        colors=cores[: len(nomes)],
        textprops={"fontsize": 11, "color": "#111111"},
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_weight("bold")

    ax.axis("equal")  # Garante que a pizza fique perfeitamente redonda
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=20, color="#111111")

    fig.canvas.draw()
    fig.savefig(caminho_arquivo, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return caminho_arquivo