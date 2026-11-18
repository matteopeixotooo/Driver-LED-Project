"""
Gera a apresentação (16:9) do trabalho de Controle Digital — Controle de Iluminação.

Saídas:
  apresentacao/apresentacao_controle_iluminacao.pdf   -> para apresentar (abre em qualquer PC)
  apresentacao/apresentacao_controle_iluminacao.pptx  -> mesma apresentação, com roteiro nas notas
  apresentacao/slides/slide_XX.png                    -> imagens individuais

Os gráficos são recalculados aqui usando as funções de simulacao_iluminacao.py.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.backends.backend_pdf import PdfPages

import simulacao_iluminacao as sim

# ------------------------------------------------------------------------------
# Estilo
# ------------------------------------------------------------------------------
W, HH = 13.333, 7.5
NAVY = "#14305A"
ACC = "#1F77B4"
ACC_LIGHT = "#EAF2FB"
GRAY = "#6B7785"
LIGHT = "#F4F6F9"
TXT = "#1E242C"
RED = "#C0392B"
RED_LIGHT = "#FDEEEC"
GREEN = "#1E8449"
GREEN_LIGHT = "#E9F7EF"
YELLOW = "#F5B700"

plt.rcParams.update({
    "font.family": ["Noto Sans", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#9AA5B1",
    "axes.labelcolor": TXT,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
})

OUT_DIR = "apresentacao"
SLIDES_DIR = os.path.join(OUT_DIR, "slides")
TOTAL_PRINCIPAL = 8


# ------------------------------------------------------------------------------
# Helpers de desenho (coordenadas em polegadas, origem no canto inferior esquerdo)
# ------------------------------------------------------------------------------
def novo_slide(titulo, kicker, num, apendice=False):
    fig = plt.figure(figsize=(W, HH))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, HH)
    ax.axis("off")

    ax.text(0.6, 6.98, kicker.upper(), fontsize=12, color=ACC, weight="bold")
    ax.text(0.6, 6.45, titulo, fontsize=28, weight="bold", color=NAVY, va="center")
    ax.plot([0.62, 1.7], [5.98, 5.98], color=ACC, lw=4, solid_capstyle="round")

    ax.text(0.6, 0.25, "Controle Digital 2026/2  ·  Controle Digital de Iluminação",
            fontsize=10, color=GRAY)
    rot = f"Apêndice {num}" if apendice else f"{num} / {TOTAL_PRINCIPAL}"
    ax.text(W - 0.6, 0.25, rot, fontsize=10, color=GRAY, ha="right")
    return fig, ax


def caixa(ax, x, y, w, h, fc=LIGHT, ec="none", lw=1.5, r=0.14, z=1):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(p)
    return p


def seta(ax, x0, y0, x1, y1, cor=NAVY, lw=2.5, ms=22):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=cor,
                                mutation_scale=ms, shrinkA=0, shrinkB=0))


def eixo(fig, x, y, w, h):
    return fig.add_axes([x / W, y / HH, w / W, h / HH])


def bloco(ax, x, y, w, h, titulo, sub=None, fc="white", ec=NAVY, tsize=15):
    caixa(ax, x, y, w, h, fc=fc, ec=ec, lw=2, r=0.12)
    if sub:
        ax.text(x + w / 2, y + h * 0.63, titulo, ha="center", va="center",
                fontsize=tsize, weight="bold", color=NAVY)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                fontsize=12, color=GRAY)
    else:
        ax.text(x + w / 2, y + h / 2, titulo, ha="center", va="center",
                fontsize=tsize, weight="bold", color=NAVY)


# ------------------------------------------------------------------------------
# Dados das simulações
# ------------------------------------------------------------------------------
def calcular_dados():
    b, a, _, _ = sim.discretizar_planta_zoh(sim.TAU_1, sim.TAU_2, sim.K_PLANTA, sim.H)
    ell_f, p_f, _, _ = sim.projetar_controlador_polinomial(b, a, [-10, -10, -25, -25], sim.H)
    ell_1, p_1, _, _ = sim.projetar_controlador_polinomial(b, a, [-18, -18, -30, -30], sim.H)

    r = 3.0
    T = 1.0
    d = {}
    d["sc"] = sim.simular_sem_controlador(lambda t: r, T)
    d["cc"] = sim.simular_com_controlador(lambda t: r, T, ell_f, p_f)
    d["t1"] = sim.simular_com_controlador(lambda t: r, T, ell_1, p_1)

    def ref_md(t):
        return 2.0 if t < 0.7 else (4.0 if t < 1.4 else 3.0)
    d["md"] = sim.simular_com_controlador(ref_md, 2.1, ell_f, p_f)

    d["m_sc"] = sim.calcular_metricas_degrau(d["sc"][0], d["sc"][2], r)
    d["m_cc"] = sim.calcular_metricas_degrau(d["cc"][0], d["cc"][2], r)
    d["m_t1"] = sim.calcular_metricas_degrau(d["t1"][0], d["t1"][2], r)
    return d


def estilo_eixo(axp, ylabel, xlabel=None):
    axp.grid(True, color="#E3E8EE", lw=0.8)
    axp.set_ylabel(ylabel)
    if xlabel:
        axp.set_xlabel(xlabel)
    else:
        axp.tick_params(labelbottom=False)


# ------------------------------------------------------------------------------
# Slides
# ------------------------------------------------------------------------------
def slide_capa():
    fig = plt.figure(figsize=(W, HH))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, HH)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), W, HH, color=NAVY))

    # "Lâmpada" decorativa
    cx, cy = 10.6, 3.9
    for rr, al in [(2.7, 0.06), (2.1, 0.10), (1.55, 0.16)]:
        ax.add_patch(Circle((cx, cy), rr, color=YELLOW, alpha=al, lw=0))
    ax.add_patch(Circle((cx, cy), 1.0, color=YELLOW, lw=0))
    ax.text(cx, cy, "300\nlux", ha="center", va="center", fontsize=26,
            weight="bold", color=NAVY, linespacing=1.0)

    ax.text(0.9, 5.55, "TRABALHO DE CONTROLE DIGITAL  ·  2026/2", fontsize=14,
            color="#8EC3F2", weight="bold")
    ax.text(0.9, 4.15, "Controle Digital de\nIluminação Adaptativa", fontsize=46,
            color="white", weight="bold", va="center", linespacing=1.1)
    ax.text(0.9, 2.55, "Driver de LED + sensor LDR, controlados por um\n"
                       "controlador digital projetado pelo Método Polinomial",
            fontsize=18, color="#D2E2F4", va="center", linespacing=1.35)
    ax.plot([0.92, 2.2], [1.65, 1.65], color=YELLOW, lw=4, solid_capstyle="round")
    ax.text(0.9, 1.1, "[Seu nome]", fontsize=16, color="white")
    return fig


def slide_planta():
    fig, ax = novo_slide("O que estamos controlando?", "1 · A planta", 2)

    yb, hb = 3.55, 1.6
    ax.text(1.35, yb + hb / 2 + 0.25, "u(t)", ha="center", fontsize=22,
            weight="bold", color=ACC)
    ax.text(1.35, yb + hb / 2 - 0.35, "tensão\n0 a 5 V", ha="center", va="center",
            fontsize=12, color=GRAY)
    seta(ax, 2.0, yb + hb / 2, 2.75, yb + hb / 2)

    bloco(ax, 2.8, yb, 3.3, hb, "Driver de LED", "transforma tensão em luz\nτ₁ = 0,05 s")
    seta(ax, 6.1, yb + hb / 2, 7.15, yb + hb / 2)
    ax.text(6.62, yb + hb / 2 + 0.3, "luz", ha="center", fontsize=12, color=GRAY)

    bloco(ax, 7.2, yb, 3.3, hb, "Sensor LDR", "transforma luz em tensão\nτ₂ = 0,15 s")
    seta(ax, 10.5, yb + hb / 2, 11.25, yb + hb / 2)
    ax.text(11.95, yb + hb / 2 + 0.25, "y(t)", ha="center", fontsize=22,
            weight="bold", color=ACC)
    ax.text(11.95, yb + hb / 2 - 0.35, "tensão medida\n1 V = 100 lux", ha="center",
            va="center", fontsize=12, color=GRAY)

    cards = [
        ("Entrada", "Tensão aplicada no driver\ndo LED (0 a 5 V)"),
        ("Saída", "Tensão do sensor LDR\n(1 V = 100 lux)"),
        ("Objetivo", "Manter a luz na bancada no\nvalor desejado (ex.: 300 lux)"),
    ]
    x = 0.6
    for tit, txt in cards:
        caixa(ax, x, 0.85, 3.85, 1.95, fc=ACC_LIGHT)
        ax.text(x + 0.3, 2.35, tit, fontsize=16, weight="bold", color=NAVY)
        ax.text(x + 0.3, 1.7, txt, fontsize=13.5, color=TXT, va="center",
                linespacing=1.4)
        x += 4.07
    return fig


def slide_modelagem():
    fig, ax = novo_slide("Das equações ao modelo", "1 · Modelagem", 3)

    y0, h0 = 1.75, 3.85
    cols = [(0.6, 3.75), (4.95, 3.75), (9.3, 3.43)]

    # Coluna 1 — equações físicas
    x, w = cols[0]
    caixa(ax, x, y0, w, h0, fc=LIGHT)
    ax.text(x + 0.25, y0 + h0 - 0.45, "Equações físicas", fontsize=16, weight="bold", color=NAVY)
    ax.text(x + 0.25, y0 + 2.75, "Driver de LED", fontsize=12.5, color=GRAY)
    ax.text(x + 0.25, y0 + 2.25, r"$\tau_1\,\dot{\Phi}(t)+\Phi(t)=K_{LED}\,u(t)$", fontsize=17, color=TXT)
    ax.text(x + 0.25, y0 + 1.55, "Sensor LDR", fontsize=12.5, color=GRAY)
    ax.text(x + 0.25, y0 + 1.05, r"$\tau_2\,\dot{y}(t)+y(t)=K_{LDR}\,\Phi(t)$", fontsize=17, color=TXT)
    ax.text(x + 0.25, y0 + 0.35, "τ₁ = 0,05 s   K_LED = 400 lux/V\nτ₂ = 0,15 s   K_LDR = 0,01 V/lux",
            fontsize=11, color=GRAY, va="center", linespacing=1.5)

    seta(ax, 4.42, y0 + h0 / 2, 4.88, y0 + h0 / 2)
    ax.text(4.65, y0 + h0 / 2 + 0.3, "Laplace", ha="center", fontsize=10.5, color=GRAY)

    # Coluna 2 — função de transferência (destaque)
    x, w = cols[1]
    caixa(ax, x, y0, w, h0, fc=ACC_LIGHT, ec=ACC, lw=2)
    ax.text(x + 0.25, y0 + h0 - 0.45, "Função de transferência", fontsize=16, weight="bold", color=NAVY)
    ax.text(x + w / 2, y0 + 2.2, r"$G(s)=\dfrac{4}{(0{,}05s+1)(0{,}15s+1)}$",
            fontsize=15.5, ha="center", va="center", color=NAVY)
    ax.text(x + w / 2, y0 + 0.95, r"$=\dfrac{533{,}3}{s^2+26{,}7\,s+133{,}3}$",
            fontsize=15, ha="center", va="center", color=TXT)

    seta(ax, 8.77, y0 + h0 / 2, 9.23, y0 + h0 / 2)

    # Coluna 3 — variáveis de estado
    x, w = cols[2]
    caixa(ax, x, y0, w, h0, fc=LIGHT)
    ax.text(x + 0.25, y0 + h0 - 0.45, "Variáveis de estado", fontsize=16, weight="bold", color=NAVY)
    ax.text(x + 0.25, y0 + 2.75, r"$x_1=y,\quad x_2=\dot{y}$", fontsize=15, color=GRAY)
    ax.text(x + 0.25, y0 + 2.1, r"$\dot{x}_1=x_2$", fontsize=16, color=TXT)
    ax.text(x + 0.25, y0 + 1.45, r"$\dot{x}_2=-133{,}3\,x_1-26{,}7\,x_2$", fontsize=16, color=TXT)
    ax.text(x + 0.25, y0 + 0.95, r"$\qquad\ \ +\,533{,}3\,u$", fontsize=16, color=TXT)
    ax.text(x + 0.25, y0 + 0.35, r"$y=x_1$", fontsize=16, color=TXT)

    chips = [("2ª ordem", NAVY), ("Estável: polos em −20 e −6,67 rad/s", NAVY),
             ("Tipo 0 (sem integrador) → erro em regime", RED)]
    x = 0.6
    larguras = [2.0, 4.6, 5.3]
    for (txt, cor), wl in zip(chips, larguras):
        caixa(ax, x, 0.8, wl, 0.62, fc="white", ec=cor, lw=1.6, r=0.3)
        ax.text(x + wl / 2, 1.11, txt, ha="center", va="center", fontsize=13, color=cor, weight="bold")
        x += wl + 0.13
    return fig


def grafico_resposta(fig, x, y, w, h, series_y, series_u, ylim_u=(-0.3, 5.6), t_max=1.0):
    h_u = h * 0.34
    h_y = h - h_u - 0.35
    ay = eixo(fig, x, y + h_u + 0.35, w, h_y)
    au = eixo(fig, x, y, w, h_u)
    for t, v, kw in series_y:
        ay.plot(t, v, **kw)
    for t, v, kw in series_u:
        au.plot(t, v, drawstyle="steps-post", **kw)
    au.axhline(5.0, color=GRAY, ls=":", lw=1.2)
    au.text(t_max * 0.995, 5.05, "limite do driver = 5 V", ha="right", va="bottom", fontsize=9.5, color=GRAY)
    ay.set_xlim(0, t_max)
    au.set_xlim(0, t_max)
    au.set_ylim(*ylim_u)
    estilo_eixo(ay, "Saída y(t) [V]")
    estilo_eixo(au, "Entrada u(t) [V]", "Tempo [s]")
    return ay, au


def slide_sem_controlador(d):
    fig, ax = novo_slide("Sem controlador, o sistema não atende", "2 · Malha fechada sem controlador", 4)
    t, r, y, u = d["sc"]
    m = d["m_sc"]

    ax.text(0.6, 5.55, "Realimentação unitária  u(t) = r(t) − y(t),  degrau de 3 V (300 lux)",
            fontsize=13, color=GRAY)
    ay, au = grafico_resposta(
        fig, 1.25, 1.0, 7.0, 4.3,
        [(t, r, dict(color="black", ls="--", lw=1.6, label="referência r(t)")),
         (t, y, dict(color=ACC, lw=2.6, label="saída y(t)"))],
        [(t, u, dict(color=RED, lw=2.0))],
    )
    ay.set_ylim(0, 3.35)
    ay.legend(loc="lower right", frameon=False, fontsize=11)
    ay.annotate("", xy=(0.75, 3.0), xytext=(0.75, 2.4),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    ay.text(0.77, 2.7, "erro de 20 %", color=RED, fontsize=12, weight="bold", va="center")
    i_pk = int(np.argmax(y))
    ay.annotate("oscila", xy=(t[i_pk], y[i_pk]), xytext=(0.27, 3.15),
                color=RED, fontsize=12, weight="bold",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6))

    problemas = [
        (f"{m['ess_pct']:.0f} %", "erro em regime", "a saída para em 2,4 V (240 lux)"),
        (f"{m['po_regime_pct']:.0f} %", "overshoot", "a luz passa do ponto e oscila"),
        (f"{m['ts_2']:.2f} s".replace(".", ","), "para acomodar", "dá para ser mais rápido"),
    ]
    yy = 3.95
    for big, mid, small in problemas:
        caixa(ax, 8.85, yy, 3.88, 1.35, fc=RED_LIGHT)
        ax.add_patch(plt.Rectangle((8.85, yy), 0.1, 1.35, color=RED))
        ax.text(9.2, yy + 0.88, big, fontsize=26, weight="bold", color=RED, va="center")
        ax.text(10.75, yy + 0.88, mid, fontsize=14.5, weight="bold", color=TXT, va="center")
        ax.text(9.2, yy + 0.33, small, fontsize=12, color=GRAY, va="center")
        yy -= 1.55
    return fig


def slide_especificacoes():
    fig, ax = novo_slide("O que eu quero e como projetei", "3 · Especificações e método", 5)

    # Especificações
    caixa(ax, 0.6, 2.35, 6.0, 3.3, fc=GREEN_LIGHT)
    ax.text(0.9, 5.2, "Especificações de desempenho", fontsize=17, weight="bold", color=GREEN)
    specs = [("Erro em regime", "0 %"), ("Overshoot (P.O.)", "≤ 5 %"),
             ("Tempo de acomodação (2 %)", "≤ 0,30 s"), ("Sinal de controle", "0 a 5 V")]
    yy = 4.6
    for lab, val in specs:
        ax.text(0.9, yy, lab, fontsize=15, color=TXT, va="center")
        ax.text(6.3, yy, val, fontsize=17, color=GREEN, weight="bold", va="center", ha="right")
        if lab != specs[-1][0]:
            ax.plot([0.9, 6.3], [yy - 0.33, yy - 0.33], color="#C9E8D5", lw=1)
        yy -= 0.66

    # Controlador e método
    caixa(ax, 6.85, 2.35, 5.88, 3.3, fc=ACC_LIGHT)
    ax.text(7.15, 5.2, "Controlador e método", fontsize=17, weight="bold", color=NAVY)
    ax.text(7.15, 4.6, "Tipo", fontsize=12, color=GRAY)
    ax.text(7.15, 4.4, "Controlador digital de 2ª ordem\ncom ação integral", fontsize=14.5,
            color=TXT, weight="bold", va="top", linespacing=1.25)
    ax.text(7.15, 3.35, "Método de projeto", fontsize=12, color=GRAY)
    ax.text(7.15, 3.15, "Polinomial (2ª Maneira): alocação de\npolos pela Equação Diofantina",
            fontsize=14.5, color=TXT, weight="bold", va="top", linespacing=1.25)

    # Diagrama da malha digital
    yc = 1.42
    ax.text(0.95, yc, "r", fontsize=17, weight="bold", color=ACC, ha="center", va="center")
    seta(ax, 1.15, yc, 1.78, yc)
    ax.add_patch(Circle((2.0, yc), 0.22, fc="white", ec=NAVY, lw=2))
    ax.text(2.0, yc, "Σ", ha="center", va="center", fontsize=13, color=NAVY)
    ax.text(1.68, yc + 0.27, "+", fontsize=12, color=NAVY)
    ax.text(2.1, yc - 0.55, "−", fontsize=14, color=NAVY)
    seta(ax, 2.22, yc, 2.9, yc)
    ax.text(2.56, yc + 0.15, "e", fontsize=12, color=GRAY, ha="center")
    bloco(ax, 2.95, yc - 0.42, 2.4, 0.84, "C(z)", fc=ACC_LIGHT, ec=ACC, tsize=16)
    ax.text(4.15, yc - 0.62, "computador (a cada h = 5 ms)", fontsize=10, color=GRAY, ha="center")
    seta(ax, 5.35, yc, 5.95, yc)
    ax.text(5.65, yc + 0.15, "u", fontsize=12, color=GRAY, ha="center")
    bloco(ax, 6.0, yc - 0.42, 1.5, 0.84, "ZOH", tsize=15)
    seta(ax, 7.5, yc, 8.1, yc)
    bloco(ax, 8.15, yc - 0.42, 2.4, 0.84, "G(s)", tsize=16)
    ax.text(9.35, yc - 0.62, "planta (LED + LDR)", fontsize=10, color=GRAY, ha="center")
    seta(ax, 10.55, yc, 11.85, yc)
    ax.text(12.1, yc, "y", fontsize=17, weight="bold", color=ACC, ha="center", va="center")
    ax.plot([11.2, 11.2, 2.0], [yc, 0.55, 0.55], color=NAVY, lw=2.2)
    seta(ax, 2.0, 0.55, 2.0, yc - 0.22)
    return fig


def slide_projeto():
    fig, ax = novo_slide("Projeto pelo Método Polinomial", "3 · Projeto do controlador", 6)

    y0, h0 = 2.55, 3.1
    passos = [
        (0.6, "1", "Escolher a amostragem"),
        (4.75, "2", "Discretizar a planta (ZOH)"),
        (8.9, "3", "Resolver a Eq. Diofantina"),
    ]
    for x, n, tit in passos:
        caixa(ax, x, y0, 3.83, h0, fc=LIGHT)
        ax.add_patch(Circle((x + 0.48, y0 + h0 - 0.45), 0.25, color=ACC))
        ax.text(x + 0.48, y0 + h0 - 0.45, n, ha="center", va="center", fontsize=14, weight="bold", color="white")
        ax.text(x + 0.88, y0 + h0 - 0.45, tit, va="center", fontsize=14.5, weight="bold", color=NAVY)

    # Passo 1
    x = 0.6
    ax.text(x + 0.3, y0 + 1.95, r"$\tau_{min}=0{,}05\ \mathrm{s}$", fontsize=16, color=TXT)
    ax.text(x + 0.3, y0 + 1.3, r"$h=\tau_{min}/10=5\ \mathrm{ms}$", fontsize=16, color=NAVY)
    ax.text(x + 0.3, y0 + 0.45, "planta simulada com passo\nΔt = τmin/100 = 0,5 ms", fontsize=11.5,
            color=GRAY, va="center", linespacing=1.35)

    # Passo 2
    x = 4.75
    ax.text(x + 3.83 / 2, y0 + 1.5, r"$G(z)=\dfrac{0{,}00638\,z+0{,}00610}{z^2-1{,}872\,z+0{,}875}$",
            fontsize=15, ha="center", va="center", color=NAVY)
    ax.text(x + 0.3, y0 + 0.45, "conversão exata da planta para\no tempo discreto", fontsize=11.5,
            color=GRAY, va="center", linespacing=1.35)

    # Passo 3
    x = 8.9
    ax.text(x + 3.83 / 2, y0 + 2.0, r"$a(z)\,\ell(z)+b(z)\,p(z)=a^*(z)$", fontsize=15,
            ha="center", color=NAVY)
    ax.text(x + 0.3, y0 + 1.35, r"$\ell(z)=(z-1)(z+\ell_0)$", fontsize=14, color=TXT)
    ax.text(x + 0.3, y0 + 1.0, "(z − 1) = integrador → erro zero", fontsize=11.5, color=GREEN, weight="bold")
    ax.text(x + 0.3, y0 + 0.45, "polos desejados (a*):\ns = −10, −10, −25, −25 rad/s", fontsize=11.5,
            color=GRAY, va="center", linespacing=1.35)

    for xa in [4.47, 8.62]:
        seta(ax, xa, y0 + h0 / 2, xa + 0.24, y0 + h0 / 2, ms=18)

    # Resultado
    caixa(ax, 0.6, 0.75, 12.13, 1.55, fc=ACC_LIGHT, ec=ACC, lw=2)
    ax.text(0.95, 1.52, "Controlador\nobtido", fontsize=15, weight="bold", color=NAVY, va="center", linespacing=1.2)
    ax.text(7.2, 1.52,
            r"$C(z)=\dfrac{U(z)}{E(z)}=\dfrac{0{,}7857\,z^2-1{,}4699\,z+0{,}6868}{z^2-1{,}8004\,z+0{,}8004}$",
            fontsize=21, ha="center", va="center", color=NAVY)
    return fig


def slide_com_controlador(d):
    fig, ax = novo_slide("Com o controlador, as metas foram atingidas", "4 · Malha fechada com controlador", 7)
    ts, rs, ysc, usc = d["sc"]
    tc, rc, ycc, ucc = d["cc"]
    msc, mcc = d["m_sc"], d["m_cc"]

    ax.text(0.6, 5.55, "Mesmo degrau de 3 V (300 lux), agora com o controlador digital C(z)",
            fontsize=13, color=GRAY)
    ay, au = grafico_resposta(
        fig, 1.25, 1.0, 7.0, 4.3,
        [(ts, rs, dict(color="black", ls="--", lw=1.6, label="referência")),
         (ts, ysc, dict(color="#AAB4BF", lw=2.0, label="sem controlador")),
         (tc, ycc, dict(color=ACC, lw=2.8, label="com controlador"))],
        [(ts, usc, dict(color="#AAB4BF", lw=1.6)),
         (tc, ucc, dict(color=RED, lw=2.0))],
    )
    ay.set_ylim(0, 3.35)
    ay.legend(loc="lower right", frameon=False, fontsize=11)

    # Tabela comparativa
    x0, y0, w0, h0 = 8.55, 0.75, 4.18, 4.95
    caixa(ax, x0, y0, w0, h0, fc=LIGHT)
    cx = [x0 + 0.2, x0 + 1.95, x0 + 2.95, x0 + 4.0]
    yy = y0 + h0 - 0.4
    for c, txt, ha in zip(cx, ["", "Sem", "Com", "Meta"], ["left", "center", "center", "right"]):
        ax.text(c, yy, txt, fontsize=13, weight="bold", color=GRAY, ha=ha, va="center")
    linhas = [
        ("Erro em\nregime", f"{msc['ess_pct']:.0f} %", f"{abs(mcc['ess_pct']):.0f} %", "0 %"),
        ("Overshoot", f"{msc['po_regime_pct']:.0f} %", f"{mcc['po_ref_pct']:.1f} %".replace(".", ","), "≤ 5 %"),
        ("Tempo de\nacomodação", f"{msc['ts_2']:.2f} s".replace(".", ","), f"{mcc['ts_2']:.2f} s".replace(".", ","), "≤ 0,30 s"),
        ("u máximo", f"{np.max(usc):.1f} V".replace(".", ","), f"{np.max(ucc):.1f} V".replace(".", ","), "≤ 5 V"),
    ]
    yy -= 0.72
    for i, (lab, s, c, meta) in enumerate(linhas):
        ax.text(cx[0], yy, lab, fontsize=12.5, color=TXT, va="center", linespacing=1.15)
        ax.text(cx[1], yy, s, fontsize=13, color=RED if lab != "u máximo" else GRAY, ha="center", va="center")
        ax.text(cx[2], yy, c, fontsize=13.5, color=GREEN, weight="bold", ha="center", va="center")
        ax.text(cx[3], yy, meta, fontsize=11.5, color=GRAY, ha="right", va="center")
        if i < len(linhas) - 1:
            ax.plot([x0 + 0.2, x0 + w0 - 0.2], [yy - 0.41, yy - 0.41], color="#DDE3EA", lw=1)
        yy -= 0.82

    caixa(ax, x0 + 0.2, y0 + 0.2, w0 - 0.4, 0.62, fc=GREEN, r=0.3)
    ax.text(x0 + w0 / 2, y0 + 0.51, "4 de 4 metas atendidas", fontsize=14, weight="bold",
            color="white", ha="center", va="center")
    return fig


def slide_conclusao(d):
    fig, ax = novo_slide("Conclusão", "Fechamento", 8)
    t, r, y, u = d["md"]

    ax.text(0.6, 5.55, "Teste extra: mudando a referência 200 → 400 → 300 lux", fontsize=13, color=GRAY)
    ap = eixo(fig, 1.25, 1.0, 6.4, 4.2)
    ap.plot(t, r, color="black", ls="--", lw=1.6, label="referência")
    ap.plot(t, y, color=ACC, lw=2.6, label="saída com controlador")
    ap.set_xlim(0, 2.1)
    ap.set_ylim(0, 4.6)
    estilo_eixo(ap, "Saída y(t) [V]", "Tempo [s]")
    ap.legend(loc="lower right", frameon=False, fontsize=11)

    itens = [
        ("Sem controlador", "erro de 20 % e oscilação de 15 %."),
        ("Método Polinomial", "com o integrador (z − 1), o erro vai a\nzero e os polos ficam onde eu escolhi."),
        ("Com controlador", "overshoot de 0,9 %, acomoda em 0,26 s\ne u sempre entre 0 e 5 V."),
    ]
    yy = 5.05
    for i, (tit, txt) in enumerate(itens, 1):
        ax.add_patch(Circle((8.4, yy - 0.05), 0.27, color=ACC))
        ax.text(8.4, yy - 0.05, str(i), ha="center", va="center", fontsize=14, weight="bold", color="white")
        ax.text(8.85, yy, tit, fontsize=15, weight="bold", color=NAVY, va="center")
        ax.text(8.85, yy - 0.3, txt, fontsize=12.5, color=TXT, va="top", linespacing=1.35)
        yy -= 1.3

    caixa(ax, 8.1, 0.75, 4.63, 0.85, fc=NAVY, r=0.3)
    ax.text(8.1 + 4.63 / 2, 1.17, "Obrigado!  Perguntas?", fontsize=18, weight="bold",
            color="white", ha="center", va="center")
    return fig


def slide_algoritmo():
    fig, ax = novo_slide("Algoritmo do controlador", "Apêndice · se perguntarem", "A", apendice=True)
    caixa(ax, 0.6, 0.75, 7.6, 4.9, fc="#1C222B", r=0.12)
    codigo = (
        "// parametros (h = 0.005 s)\n"
        "ell1 = -1.800410;   ell0 = 0.800410;\n"
        "p2 = 0.785669;  p1 = -1.469869;  p0 = 0.686831;\n"
        "uant1 = uant2 = eant1 = eant2 = 0;\n"
        "\n"
        "while (loop)            // a cada h = 5 ms\n"
        "{\n"
        "   y = vin1();          // le o sensor (A/D)\n"
        "   e = r - y;           // erro\n"
        "   u = -ell1*uant1 - ell0*uant2\n"
        "       + p2*e + p1*eant1 + p0*eant2;\n"
        "   uant2 = uant1;  uant1 = u;\n"
        "   eant2 = eant1;  eant1 = e;\n"
        "   vout1(u);            // envia ao driver (D/A)\n"
        "}"
    )
    ax.text(0.9, 5.35, codigo, family="DejaVu Sans Mono", fontsize=12.5, color="#E6EDF3",
            va="top", linespacing=1.45)

    caixa(ax, 8.45, 0.75, 4.28, 4.9, fc=LIGHT)
    ax.text(8.75, 5.2, "Equação a diferenças", fontsize=15, weight="bold", color=NAVY)
    ax.text(8.75, 4.55, r"$u(k)=1{,}8004\,u(k-1)-0{,}8004\,u(k-2)$", fontsize=12.5, color=TXT)
    ax.text(8.75, 4.1, r"$\quad+\,0{,}7857\,e(k)-1{,}4699\,e(k-1)$", fontsize=12.5, color=TXT)
    ax.text(8.75, 3.65, r"$\quad+\,0{,}6868\,e(k-2)$", fontsize=12.5, color=TXT)
    bullets = ["• Usa só a amostra atual e as 2\n   anteriores (causal).",
               "• 5 multiplicações e 4 somas a\n   cada 5 ms.",
               "• Entre amostras, u fica constante\n   (ZOH = 10 passos de simulação)."]
    for i, b in enumerate(bullets):
        ax.text(8.75, 3.0 - 0.75 * i, b, fontsize=12, color=TXT, va="top", linespacing=1.25)
    return fig


def slide_tentativa(d):
    fig, ax = novo_slide("Por que ajustei os polos?", "Apêndice · se perguntarem", "B", apendice=True)
    t1, r1, y1, u1 = d["t1"]
    tc, rc, yc, uc = d["cc"]
    m1, mc = d["m_t1"], d["m_cc"]

    ay, au = grafico_resposta(
        fig, 1.25, 1.0, 7.0, 4.6,
        [(t1, r1, dict(color="black", ls="--", lw=1.6, label="referência")),
         (t1, y1, dict(color="#E67E22", lw=2.2, label="1ª tentativa (−18, −30)")),
         (tc, yc, dict(color=ACC, lw=2.6, label="final (−10, −25)"))],
        [(t1, u1, dict(color="#E67E22", lw=1.8)),
         (tc, uc, dict(color=RED, lw=2.0))],
        ylim_u=(-0.3, 7.8),
    )
    ay.set_ylim(0, 3.5)
    ay.legend(loc="lower right", frameon=False, fontsize=11)

    caixa(ax, 8.75, 3.3, 3.98, 2.35, fc="#FEF5E7")
    ax.text(9.05, 5.2, "1ª tentativa: polos rápidos", fontsize=14, weight="bold", color="#B9770E")
    ax.text(9.05, 4.75, f"• overshoot de {m1['po_ref_pct']:.1f} % (> 5 %)\n"
                        f"• u chega a {np.max(u1):.1f} V (> 5 V)".replace(".", ","),
            fontsize=12.5, color=TXT, va="top", linespacing=1.5)
    ax.text(9.05, 3.7, "os zeros de p(z) aumentam o pico", fontsize=11, color=GRAY)

    caixa(ax, 8.75, 0.75, 3.98, 2.35, fc=GREEN_LIGHT)
    ax.text(9.05, 2.65, "Ajuste: polos mais suaves", fontsize=14, weight="bold", color=GREEN)
    ax.text(9.05, 2.2, f"• overshoot de {mc['po_ref_pct']:.1f} %\n"
                       f"• u máximo de {np.max(uc):.1f} V\n"
                       f"• acomoda em {mc['ts_2']:.2f} s".replace(".", ","),
            fontsize=12.5, color=TXT, va="top", linespacing=1.5)
    return fig


# ------------------------------------------------------------------------------
# Roteiro (vai para as notas do PPTX e para roteiro_apresentacao.md)
# ------------------------------------------------------------------------------
ROTEIRO = [
    ("Capa", "20 s",
     "Bom dia. Meu trabalho é o controle digital de um sistema de iluminação: um driver de LED "
     "e um sensor LDR, controlados por um controlador digital que eu projetei pelo Método Polinomial."),
    ("A planta", "1 min",
     "A planta é uma luminária de LED iluminando uma bancada. A entrada é a tensão no driver, de 0 a 5 V. "
     "O driver transforma tensão em luz, com constante de tempo de 0,05 s. O sensor LDR mede essa luz e "
     "devolve uma tensão, com constante de tempo de 0,15 s, calibrado para 1 V igual a 100 lux. "
     "O objetivo é manter a luz na bancada no valor desejado, por exemplo 300 lux."),
    ("Modelagem", "1 min 15 s",
     "Cada bloco é modelado por uma equação diferencial de primeira ordem. Aplicando Laplace e juntando os dois, "
     "cheguei na função de transferência G(s) = 4 / [(0,05s + 1)(0,15s + 1)]. "
     "Na forma de variáveis de estado, uso x1 = y e x2 = derivada de y, que é o que eu integro na simulação. "
     "É uma planta de 2ª ordem, estável, com polos em −20 e −6,67, e do tipo 0, sem integrador. "
     "Por isso já dá para esperar erro em regime na malha fechada."),
    ("Malha fechada sem controlador", "1 min 15 s",
     "Simulando em malha fechada sem controlador, ou seja, u = r − y, com degrau de 3 V: "
     "aparecem três problemas. Primeiro, erro em regime de 20 %: a saída para em 2,4 V. "
     "Segundo, overshoot de 15 %: a luz passa do ponto e oscila. "
     "Terceiro, leva 0,31 s para acomodar."),
    ("Especificações e método", "1 min 15 s",
     "Então defini as especificações: erro em regime zero, overshoot de no máximo 5 %, "
     "tempo de acomodação de até 0,30 s e sinal de controle entre 0 e 5 V, que é o limite do driver. "
     "Projetei um controlador digital de 2ª ordem com ação integral pelo Método Polinomial. "
     "Embaixo está a malha: o computador calcula C(z) a cada 5 ms, o ZOH segura o valor e aplica na planta."),
    ("Projeto pelo Método Polinomial", "1 min 30 s",
     "O projeto teve três passos. Um: a menor constante de tempo é 0,05 s, então pela regra do trabalho "
     "a amostragem é h = τmin/10 = 5 ms, e a planta é simulada com passo de 0,5 ms. "
     "Dois: discretizei a planta pelo ZOH e obtive G(z). "
     "Três: resolvi a Equação Diofantina. Coloquei o fator (z − 1) em ℓ(z), que é o integrador "
     "e garante erro zero ao degrau, e escolhi os polos desejados em −10, −10, −25 e −25. "
     "Resolvendo, chego nesse controlador C(z)."),
    ("Malha fechada com controlador", "1 min 30 s",
     "Com o controlador, a curva azul é a nova resposta e a cinza é a antiga, sem controlador. "
     "O erro em regime foi de 20 % para zero, o overshoot de 15 % para 0,9 %, "
     "o tempo de acomodação de 0,31 para 0,26 s, e o sinal de controle ficou no máximo em 2,4 V, "
     "dentro do limite de 5 V. Ou seja, as quatro especificações foram atendidas."),
    ("Conclusão", "45 s",
     "Para fechar, testei mudando a referência para 200, 400 e 300 lux, e o controlador segue todos os degraus "
     "sem erro. Resumindo: sem controlador havia erro de 20 % e oscilação; com o Método Polinomial e o "
     "integrador, o erro foi a zero e a resposta ficou rápida e sem oscilação. Obrigado."),
    ("Apêndice A — Algoritmo", "só se perguntarem",
     "Este é o algoritmo: a cada 5 ms lê o sensor, calcula o erro, calcula u com a equação a diferenças, "
     "atualiza as variáveis passadas e envia u para o driver."),
    ("Apêndice B — Ajuste dos polos", "só se perguntarem",
     "Na primeira tentativa usei polos mais rápidos, −18 e −30. O erro zerou, mas o overshoot foi 8,8 % e o "
     "sinal de controle passou de 7 V, acima do limite de 5 V. Suavizei os polos para −10 e −25 e todas as "
     "especificações foram atendidas."),
]


def salvar_roteiro():
    linhas = ["# Roteiro da apresentação (≈ 9 min)\n",
              "Fale com calma; o tempo entre parênteses é uma referência.\n"]
    for i, (tit, tempo, fala) in enumerate(ROTEIRO, 1):
        rot = f"Slide {i}" if i <= TOTAL_PRINCIPAL else "Extra"
        linhas.append(f"\n## {rot} — {tit} ({tempo})\n\n{fala}\n")
    with open(os.path.join(OUT_DIR, "roteiro_apresentacao.md"), "w", encoding="utf-8") as f:
        f.write("".join(linhas))


def salvar_pptx(pngs):
    try:
        from pptx import Presentation
        from pptx.util import Inches
    except ImportError:
        print("python-pptx não instalado: PPTX não gerado (o PDF já serve para apresentar).")
        return
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(HH)
    for png, (tit, tempo, fala) in zip(pngs, ROTEIRO):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(png, 0, 0, width=prs.slide_width, height=prs.slide_height)
        s.notes_slide.notes_text_frame.text = f"{tit} ({tempo})\n\n{fala}"
    prs.save(os.path.join(OUT_DIR, "apresentacao_controle_iluminacao.pptx"))


def main():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    d = calcular_dados()
    figs = [
        slide_capa(),
        slide_planta(),
        slide_modelagem(),
        slide_sem_controlador(d),
        slide_especificacoes(),
        slide_projeto(),
        slide_com_controlador(d),
        slide_conclusao(d),
        slide_algoritmo(),
        slide_tentativa(d),
    ]
    pngs = []
    with PdfPages(os.path.join(OUT_DIR, "apresentacao_controle_iluminacao.pdf")) as pdf:
        for i, fig in enumerate(figs, 1):
            png = os.path.join(SLIDES_DIR, f"slide_{i:02d}.png")
            fig.savefig(png, dpi=150)
            pdf.savefig(fig)
            plt.close(fig)
            pngs.append(png)
    salvar_pptx(pngs)
    salvar_roteiro()
    print(f"{len(figs)} slides gerados em ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
