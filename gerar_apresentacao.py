"""
Gera a apresentação (16:9, <= 10 min) do trabalho de Controle Digital — Controle de Iluminação.

Inclui as deduções matemáticas completas ensinadas em aula:
  - Modelagem física -> Laplace -> G(s) e Variáveis de Estado (Aula 11)
  - Análise em Malha Fechada sem controlador: wn, zeta, P.O. e Teorema do Valor Final (Aula 07)
  - Discretização exata por Equivalência do ZOH via Frações Parciais (Aula 08)
  - Método Polinomial: coprimalidade, Princípio do Modelo Interno, graus, a*(z) e sistema 4x4 (Aula 10)
  - Conversão por z^-2 -> Equação a Diferenças -> Algoritmo + ZOH (Aula 10)

Saídas (pasta apresentacao/):
  apresentacao_controle_iluminacao.pdf   -> para apresentar
  apresentacao_controle_iluminacao.pptx  -> mesmos slides + roteiro de fala nas notas
  roteiro_apresentacao.md                -> o que falar em cada slide
  slides/slide_XX.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Rectangle
from matplotlib.backends.backend_pdf import PdfPages

import simulacao_iluminacao as sim

# ------------------------------------------------------------------------------
# Configuração
# ------------------------------------------------------------------------------
NOME = "Matteo Peixoto"
URL_SIMULADOR = "https://matteopeixotooo.github.io/Driver-LED-Project/"

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
ORANGE = "#E67E22"
ORANGE_LIGHT = "#FEF5E7"

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
ETAPAS = ["Planta", "Sem controlador", "Projeto", "Com controlador"]


def br(v, dec=2):
    return f"{v:.{dec}f}".replace(".", ",")


def caixa(ax, x, y, w, h, fc=LIGHT, ec="none", lw=1.5, r=0.14, z=1):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(p)
    return p


def seta(ax, x0, y0, x1, y1, cor=NAVY, lw=2.5, ms=20, ls="-"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=cor, ls=ls,
                                mutation_scale=ms, shrinkA=0, shrinkB=0))


def eixo(fig, x, y, w, h):
    return fig.add_axes([x / W, y / HH, w / W, h / HH])


def bloco(ax, x, y, w, h, titulo, sub=None, fc="white", ec=NAVY, tsize=15):
    caixa(ax, x, y, w, h, fc=fc, ec=ec, lw=2, r=0.12)
    if sub:
        ax.text(x + w / 2, y + h * 0.64, titulo, ha="center", va="center",
                fontsize=tsize, weight="bold", color=NAVY)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                fontsize=11.5, color=GRAY)
    else:
        ax.text(x + w / 2, y + h / 2, titulo, ha="center", va="center",
                fontsize=tsize, weight="bold", color=NAVY)


def novo_slide(titulo, num, total, etapa=None, resumo=None):
    fig = plt.figure(figsize=(W, HH))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, HH)
    ax.axis("off")

    x = 0.6
    for i, nome in enumerate(ETAPAS, 1):
        ativo = (etapa == i)
        feito = etapa is not None and i < etapa
        larg = 0.42 + 0.105 * len(nome)
        fc = NAVY if ativo else ("#D6E4F3" if feito else "#EEF1F5")
        tc = "white" if ativo else (NAVY if feito else "#9AA5B1")
        caixa(ax, x, 6.88, larg, 0.36, fc=fc, r=0.18)
        ax.text(x + larg / 2, 7.06, f"{i}  {nome}", ha="center", va="center",
                fontsize=10.5, color=tc, weight="bold")
        x += larg + 0.1

    ax.text(0.6, 6.28, titulo, fontsize=26, weight="bold", color=NAVY, va="center")
    ax.plot([0.62, 1.7], [5.86, 5.86], color=ACC, lw=4, solid_capstyle="round")

    if resumo:
        caixa(ax, 0.6, 0.48, 12.13, 0.58, fc=ACC_LIGHT, r=0.12)
        ax.add_patch(Rectangle((0.6, 0.48), 0.09, 0.58, color=ACC))
        ax.text(0.88, 0.77, "Resumo:", fontsize=13, weight="bold", color=NAVY, va="center")
        ax.text(1.92, 0.77, resumo, fontsize=13, color=TXT, va="center")

    ax.text(0.6, 0.17, f"{NOME}  ·  Controle Digital 2026/2  ·  Controle Digital de Iluminação",
            fontsize=9.5, color=GRAY)
    ax.text(W - 0.6, 0.17, f"{num} / {total}", fontsize=9.5, color=GRAY, ha="right")
    return fig, ax


def estilo_eixo(axp, ylabel, xlabel=None):
    axp.grid(True, color="#E3E8EE", lw=0.8)
    axp.set_ylabel(ylabel)
    if xlabel:
        axp.set_xlabel(xlabel)
    else:
        axp.tick_params(labelbottom=False)


def grafico_resposta(fig, x, y, w, h, series_y, series_u, ylim_y=(0, 3.4),
                     ylim_u=(-0.3, 5.7), t_max=1.0):
    h_u = h * 0.34
    h_y = h - h_u - 0.28
    ay = eixo(fig, x, y + h_u + 0.28, w, h_y)
    au = eixo(fig, x, y, w, h_u)
    for t, v, kw in series_y:
        ay.plot(t, v, **kw)
    for t, v, kw in series_u:
        au.plot(t, v, drawstyle="steps-post", **kw)
    au.axhline(5.0, color=GRAY, ls=":", lw=1.2)
    au.text(t_max * 0.995, 5.08, "limite do driver = 5 V", ha="right", va="bottom",
            fontsize=9.5, color=GRAY)
    ay.set_xlim(0, t_max)
    au.set_xlim(0, t_max)
    ay.set_ylim(*ylim_y)
    au.set_ylim(*ylim_u)
    estilo_eixo(ay, "Saída y(t) [V]")
    estilo_eixo(au, "Entrada u(t) [V]", "Tempo [s]")
    return ay, au


def qr_image(url):
    import qrcode
    q = qrcode.QRCode(border=1, box_size=10)
    q.add_data(url)
    q.make(fit=True)
    img = q.make_image(fill_color=NAVY, back_color="white").convert("RGB")
    return np.asarray(img)


def calcular_dados():
    b, a, _, _ = sim.discretizar_planta_zoh(sim.TAU_1, sim.TAU_2, sim.K_PLANTA, sim.H)
    ell_f, p_f, _, _ = sim.projetar_controlador_polinomial(b, a, [-10, -10, -25, -25], sim.H)
    ell_1, p_1, _, _ = sim.projetar_controlador_polinomial(b, a, [-18, -18, -30, -30], sim.H)

    r = 3.0
    d = {"b": b, "a": a, "ell": ell_f, "p": p_f}
    d["sc"] = sim.simular_sem_controlador(lambda t: r, 1.0)
    d["cc"] = sim.simular_com_controlador(lambda t: r, 1.0, ell_f, p_f)
    d["t1"] = sim.simular_com_controlador(lambda t: r, 1.0, ell_1, p_1)

    d["m_sc"] = sim.calcular_metricas_degrau(d["sc"][0], d["sc"][2], r)
    d["m_cc"] = sim.calcular_metricas_degrau(d["cc"][0], d["cc"][2], r)
    d["m_t1"] = sim.calcular_metricas_degrau(d["t1"][0], d["t1"][2], r)
    return d


# ------------------------------------------------------------------------------
# Slides
# ------------------------------------------------------------------------------
def s_capa():
    fig = plt.figure(figsize=(W, HH))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, HH)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, HH, color=NAVY))

    ax.text(0.9, 5.75, "TRABALHO DE CONTROLE DIGITAL  ·  2026/2", fontsize=14,
            color="#8EC3F2", weight="bold")
    ax.text(0.9, 4.45, "Controle Digital\nde Iluminação", fontsize=50,
            color="white", weight="bold", va="center", linespacing=1.08)
    ax.text(0.9, 2.85, "Mantendo a luz de uma bancada em 300 lux com\n"
                       "um driver de LED, um sensor LDR e Método Polinomial",
            fontsize=18, color="#D2E2F4", va="center", linespacing=1.35)
    ax.plot([0.92, 2.2], [1.95, 1.95], color=YELLOW, lw=4, solid_capstyle="round")
    ax.text(0.9, 1.4, NOME, fontsize=18, color="white", weight="bold")

    caixa(ax, 9.25, 1.55, 3.3, 4.35, fc="white", r=0.2)
    ax_qr = eixo(fig, 9.6, 2.45, 2.6, 2.6)
    ax_qr.imshow(qr_image(URL_SIMULADOR), interpolation="nearest")
    ax_qr.axis("off")
    ax.text(10.9, 5.45, "Simulador + Slides online", ha="center", fontsize=14, weight="bold", color=NAVY)
    ax.text(10.9, 2.05, URL_SIMULADOR.replace("https://", ""), ha="center", fontsize=9, color=GRAY)
    return fig


def s_planta(num, total):
    fig, ax = novo_slide("A planta: controle de iluminação em bancada", num, total, etapa=1,
                         resumo="entrada u = tensão no driver LED (0 a 5 V)  ·  saída y = tensão do sensor LDR (1 V = 100 lux)")

    caixa(ax, 0.6, 1.3, 6.4, 4.3, fc="#FAFBFD", ec="#E1E6ED", lw=1.2)
    ax.add_patch(Polygon([(2.15, 4.62), (3.35, 4.62), (4.55, 2.05), (0.95, 2.05)],
                         closed=True, fc=YELLOW, alpha=0.22, lw=0))
    ax.text(2.75, 3.1, "300 lux", ha="center", fontsize=17, weight="bold", color="#9A7300")
    ax.plot([2.75, 2.75], [5.0, 5.52], color=NAVY, lw=2)
    ax.add_patch(Polygon([(2.1, 4.65), (3.4, 4.65), (3.05, 5.02), (2.45, 5.02)],
                         closed=True, fc=NAVY, lw=0))
    ax.add_patch(Rectangle((2.2, 4.58), 1.1, 0.08, color=YELLOW))
    ax.text(1.95, 4.9, "LED", ha="right", fontsize=13, weight="bold", color=NAVY)
    ax.add_patch(Rectangle((0.9, 1.85), 4.6, 0.2, color="#8D9AA8"))
    ax.add_patch(Rectangle((1.1, 1.45), 0.12, 0.4, color="#8D9AA8"))
    ax.add_patch(Rectangle((5.18, 1.45), 0.12, 0.4, color="#8D9AA8"))
    ax.text(1.5, 1.6, "bancada", fontsize=11, color=GRAY)
    ax.add_patch(Circle((4.1, 2.17), 0.12, color=RED, zorder=4))
    ax.text(4.1, 2.45, "sensor LDR", ha="center", fontsize=11.5, weight="bold", color=RED)

    bloco(ax, 5.25, 3.45, 1.55, 0.95, "Controlador", "A/D + D/A", fc=ACC_LIGHT, ec=ACC, tsize=12.5)
    ax.plot([4.25, 6.02, 6.02], [2.17, 2.17, 3.45], color=ACC, lw=2.2, ls="--")
    seta(ax, 6.02, 3.0, 6.02, 3.42, cor=ACC, lw=2.2, ms=16)
    ax.text(6.15, 2.6, "mede y", fontsize=11, color=ACC, weight="bold")
    ax.plot([5.25, 3.6], [4.15, 4.83], color=RED, lw=2.2)
    seta(ax, 3.9, 4.71, 3.45, 4.88, cor=RED, lw=2.2, ms=16)
    ax.text(4.55, 4.75, "atua u", fontsize=11, color=RED, weight="bold", rotation=-22)

    xt = 7.35
    itens = [
        ("O sistema físico", "Luminária LED controlada por driver PWM filtrado\n(τ₁ = 0,05 s) e medida por sensor LDR (τ₂ = 0,15 s)."),
        ("Linearização", "Operando na faixa linear calibrada (0 a 500 lux),\nonde 1 V no sensor equivale a 100 lux na bancada."),
        ("Objetivo", "Manter a iluminância em 300 lux (r = 3,0 V)\nsem oscilações e sem erro em regime permanente."),
    ]
    yy = 5.3
    for tit, txt in itens:
        ax.text(xt, yy, tit, fontsize=15.5, weight="bold", color=NAVY, va="center")
        ax.text(xt, yy - 0.4, txt, fontsize=12.5, color=TXT, va="top", linespacing=1.4)
        yy -= 1.38
    return fig


def s_modelagem(num, total):
    fig, ax = novo_slide("Modelagem: EDOs → Função de Transferência → Estados", num, total, etapa=1,
                         resumo="sistema de 2ª ordem, Tipo 0, estável em malha aberta com polos reais em s = −20 e s = −6,67 rad/s")

    y0, h0 = 1.28, 4.35
    cols = [(0.6, 4.05, "① Equações + Laplace"), (4.92, 4.15, "② Função de Transferência"),
            (9.34, 3.39, "③ Variáveis de Estado")]
    for i, (x, w, tit) in enumerate(cols):
        dest = (i == 1)
        caixa(ax, x, y0, w, h0, fc=ACC_LIGHT if dest else LIGHT,
              ec=ACC if dest else "none", lw=2)
        ax.text(x + 0.22, y0 + h0 - 0.36, tit, fontsize=14, weight="bold", color=NAVY)
    seta(ax, 4.68, y0 + h0 / 2, 4.89, y0 + h0 / 2, ms=16)
    seta(ax, 9.10, y0 + h0 / 2, 9.31, y0 + h0 / 2, ms=16)

    # Coluna 1
    x = 0.82
    ax.text(x, 4.88, "Driver LED (τ₁ = 0,05 s; K_LED = 400 lux/V):", fontsize=10.5, color=GRAY)
    ax.text(x, 4.42, r"$\tau_1\,\dot{\Phi}+\Phi=K_{LED}\,u \;\Rightarrow\; \dfrac{\Phi(s)}{U(s)}=\dfrac{400}{0{,}05s+1}$",
            fontsize=11.5, color=TXT)
    ax.text(x, 3.65, "Sensor LDR (τ₂ = 0,15 s; K_LDR = 0,01 V/lux):", fontsize=10.5, color=GRAY)
    ax.text(x, 3.18, r"$\tau_2\,\dot{y}+y=K_{LDR}\,\Phi \;\Rightarrow\; \dfrac{Y(s)}{\Phi(s)}=\dfrac{0{,}01}{0{,}15s+1}$",
            fontsize=11.5, color=TXT)
    ax.text(x, 2.15, "Multiplicando os blocos em série:\n"
                     r"$K = K_{LED}\cdot K_{LDR} = 400 \times 0{,}01 = 4{,}0\ \mathrm{V/V}$",
            fontsize=11, color=NAVY, va="center", linespacing=1.45)

    # Coluna 2
    xc = 4.92 + 4.15 / 2
    ax.text(xc, 4.58, r"$G(s)=\dfrac{Y(s)}{U(s)}=\dfrac{4{,}0}{(0{,}05s+1)(0{,}15s+1)}$",
            fontsize=13.5, ha="center", va="center", color=NAVY)
    ax.text(xc, 3.62, r"$=\dfrac{4{,}0}{0{,}0075\,s^2+0{,}20\,s+1}$",
            fontsize=13, ha="center", va="center", color=TXT)
    ax.text(xc, 2.68, r"$=\dfrac{533{,}33}{(s+20)(s+6{,}67)}=\dfrac{533{,}33}{s^2+26{,}67s+133{,}33}$",
            fontsize=12.5, ha="center", va="center", color=NAVY)
    ax.text(5.15, 1.65, "• Polos em malha aberta: s₁ = −20, s₂ = −6,67 rad/s\n"
                        "• Planta Tipo 0 (sem polo em s = 0)",
            fontsize=10.8, color=TXT, va="center", linespacing=1.45)

    # Coluna 3
    x = 9.54
    ax.text(x, 4.78, r"Estados: $x_1=y,\quad x_2=\dot{y}$", fontsize=12, color=GRAY)
    ax.text(x, 4.15, r"$\dot{x}_1 = x_2$", fontsize=13.5, color=TXT)
    ax.text(x, 3.55, r"$\dot{x}_2 = -133{,}33\,x_1 - 26{,}67\,x_2 + 533{,}33\,u$", fontsize=11.5, color=TXT)
    # Matriz de estados desenhada com colchetes limpos
    ax.text(x, 2.72, r"$\dot{x}=$", fontsize=12, color=NAVY, va="center")
    for bx, bw in [(x + 0.45, 1.38), (x + 2.18, 0.62)]:
        ax.plot([bx + 0.06, bx, bx, bx + 0.06], [3.08, 3.08, 2.36, 2.36], color=NAVY, lw=1.4)
        ax.plot([bx + bw - 0.06, bx + bw, bx + bw, bx + bw - 0.06], [3.08, 3.08, 2.36, 2.36], color=NAVY, lw=1.4)
    ax.text(x + 1.14, 2.90, "0        1", ha="center", va="center", fontsize=10.5, color=NAVY)
    ax.text(x + 1.14, 2.54, "−133,33  −26,67", ha="center", va="center", fontsize=10.2, color=NAVY)
    ax.text(x + 1.98, 2.72, r"$x+$", ha="center", va="center", fontsize=12, color=NAVY)
    ax.text(x + 2.49, 2.90, "0", ha="center", va="center", fontsize=10.5, color=NAVY)
    ax.text(x + 2.49, 2.54, "533,33", ha="center", va="center", fontsize=10.2, color=NAVY)
    ax.text(x + 2.90, 2.72, r"$u$", ha="center", va="center", fontsize=12, color=NAVY)
    ax.text(x, 1.95, r"$y = [\,1 \quad 0\,]\,x$", fontsize=12.5, color=NAVY)
    ax.text(x, 1.45, "Integrada via RK4 (Δt = τ_min/100)", fontsize=10, color=GRAY)
    return fig


def s_analise_mf_sem_ctrl(num, total):
    fig, ax = novo_slide("Análise Analítica em Malha Fechada (sem controlador)", num, total, etapa=2,
                         resumo="as contas da Aula 07 preveem exatamente o que ocorre na simulação: erro de 20% e P.O. ≈ 15%")

    # Caixa esquerda: FT em malha fechada
    caixa(ax, 0.6, 1.32, 5.95, 4.3, fc=LIGHT)
    ax.text(0.88, 5.22, "1. Função de Transferência em Malha Fechada (C(s) = 1)",
            fontsize=13.5, weight="bold", color=NAVY)
    ax.text(3.55, 4.45, r"$G_{MF}(s)=\dfrac{G(s)}{1+G(s)}=\dfrac{533{,}33}{s^2+26{,}67s+133{,}33+533{,}33}$",
            fontsize=12.5, ha="center", va="center", color=NAVY)
    ax.text(3.55, 3.55, r"$G_{MF}(s)=\dfrac{533{,}33}{s^2+26{,}67s+666{,}67}$",
            fontsize=15.5, ha="center", va="center", color=ACC)

    ax.text(0.88, 2.75, "Comparando com a forma padrão de 2ª ordem:", fontsize=11.5, color=GRAY)
    ax.text(0.88, 2.25, r"$\omega_n = \sqrt{666{,}67} = 25{,}82\ \mathrm{rad/s}$", fontsize=13.5, color=TXT)
    ax.text(0.88, 1.7, r"$2\zeta\omega_n = 26{,}67 \;\Rightarrow\; \zeta = \dfrac{26{,}67}{2\cdot 25{,}82} = 0{,}5164 < 1$",
            fontsize=13, color=RED)

    # Caixa direita: Previsão de P.O. e e_ss
    caixa(ax, 6.8, 1.32, 5.93, 4.3, fc=RED_LIGHT, ec=RED, lw=1.6)
    ax.text(7.08, 5.22, "2. Diagnóstico Analítico (degrau r = 3,0 V)",
            fontsize=13.5, weight="bold", color=RED)

    ax.text(7.08, 4.55, "Ultrapassagem Percentual (P.O.):", fontsize=12, weight="bold", color=NAVY)
    ax.text(7.08, 3.95, r"$P.O. = e^{-\pi\zeta/\sqrt{1-\zeta^2}}\times 100\% = 15{,}04\%$",
            fontsize=13.5, color=TXT)

    ax.text(7.08, 3.2, "Erro em Regime Permanente (Teorema do Valor Final):", fontsize=12, weight="bold", color=NAVY)
    ax.text(7.08, 2.55, r"$y(\infty)=\lim_{s\to 0}\, s\cdot G_{MF}(s)\cdot\dfrac{3}{s}=\dfrac{533{,}33}{666{,}67}\cdot 3 = 2{,}40\ \mathrm{V}$",
            fontsize=12.5, color=TXT)
    ax.text(7.08, 1.72, r"$e_{ss} = \dfrac{3{,}0 - 2{,}40}{3{,}0} = 20{,}0\% \quad (\text{devido ao Tipo } 0)$",
            fontsize=13.5, color=RED)
    return fig


def s_sem_controlador(d, num, total):
    fig, ax = novo_slide("Simulação em Malha Fechada SEM Controlador", num, total, etapa=2,
                         resumo="a simulação confirma as contas: erro de 20,00% (2,40 V vs 3,00 V) e P.O. de 15,24%")
    t, r, y, u = d["sc"]
    m = d["m_sc"]

    ax.text(0.6, 5.45, "Integração RK4 com Δt = τ_min/100 = 0,0005 s  |  u(t) = r(t) − y(t)  |  r = 3,0 V (300 lux)",
            fontsize=12, color=GRAY)
    ay, au = grafico_resposta(
        fig, 1.25, 1.32, 6.9, 3.85,
        [(t, r, dict(color="black", ls="--", lw=1.6, label="referência r(t)")),
         (t, y, dict(color=ACC, lw=2.6, label="saída y(t)"))],
        [(t, u, dict(color=RED, lw=2.0))])
    ay.legend(loc="lower right", frameon=False, fontsize=10.5)
    ay.annotate("", xy=(0.72, 3.0), xytext=(0.72, 2.4),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    ay.text(0.74, 2.7, "e_ss = 20%", color=RED, fontsize=11, weight="bold", va="center")
    i_pk = int(np.argmax(y))
    ay.annotate("P.O. = 15,24%", xy=(t[i_pk], y[i_pk]), xytext=(0.28, 3.16), color=RED, fontsize=11,
                weight="bold", arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.5))

    problemas = [
        (f"{m['ess_pct']:.0f} %", "erro em regime", "para em 2,40 V (240 lux)\nem vez de 3,00 V (300 lux)"),
        (f"{br(m['po_regime_pct'], 1)} %", "de overshoot", "pico em 2,77 V; oscila\nantes de estabilizar"),
        (f"{br(m['ts_2'])} s", "acomodação Ts(2%)", "pode ficar mais rápido\nsem ultrapassar 5%"),
    ]
    yy = 5.05
    for big, mid, small in problemas:
        caixa(ax, 8.55, yy - 1.05, 4.18, 1.12, fc=RED_LIGHT)
        ax.add_patch(Rectangle((8.55, yy - 1.05), 0.09, 1.12, color=RED))
        ax.text(8.8, yy - 0.48, big, fontsize=21, weight="bold", color=RED, va="center")
        ax.text(10.35, yy - 0.3, mid, fontsize=12.5, weight="bold", color=TXT, va="center")
        ax.text(10.35, yy - 0.72, small, fontsize=10.2, color=GRAY, va="center", linespacing=1.2)
        yy -= 1.25
    return fig


def s_especificacoes(num, total):
    fig, ax = novo_slide("Especificações Desejadas e Escolha do Método", num, total, etapa=3,
                         resumo="Segunda Maneira + Método Polinomial (Aula 10): projeta C(z) direto no plano z com integrador (z−1)")

    # Metas (esquerda)
    caixa(ax, 0.6, 1.32, 5.75, 4.28, fc=GREEN_LIGHT)
    ax.text(0.88, 5.2, "Especificações de Desempenho", fontsize=15.5, weight="bold", color=GREEN)
    specs = [
        ("Erro em regime (e_ss)", "0 %", "exige ação integral"),
        ("Ultrapassagem (P.O.)", "≤ 5,0 %", "evita sobrebrilho visível"),
        ("Acomodação Ts (2%)", "≤ 0,30 s", "mais rápido que sem ctrl"),
        ("Sinal de controle u(t)", "0 a 5,0 V", "faixa física do driver LED"),
    ]
    yy = 4.55
    for lab, meta, obs in specs:
        ax.text(0.88, yy, lab, fontsize=13, weight="bold", color=TXT)
        ax.text(6.05, yy, meta, fontsize=15, weight="bold", color=GREEN, ha="right")
        ax.text(0.88, yy - 0.32, obs, fontsize=10.5, color=GRAY)
        if lab != specs[-1][0]:
            ax.plot([0.88, 6.05], [yy - 0.52, yy - 0.52], color="#C8E6D2", lw=1)
        yy -= 0.86

    # Método (direita)
    caixa(ax, 6.6, 1.32, 6.13, 4.28, fc=ACC_LIGHT, ec=ACC, lw=1.6)
    ax.text(6.88, 5.2, "Abordagem: 2ª Maneira — Método Polinomial", fontsize=14.5, weight="bold", color=NAVY)
    ax.text(6.88, 4.68, "Planta Contínua G(s)  →  Discretização ZOH G(z)  →  Projeto Discreto C(z)",
            fontsize=11, weight="bold", color=ACC)

    ax.text(6.88, 4.12, "Função de transferência em malha fechada:", fontsize=11.5, color=GRAY)
    ax.text(9.66, 3.55, r"$\dfrac{Y(z)}{R(z)} = \dfrac{p(z)\,b(z)}{a(z)\,\ell(z) + b(z)\,p(z)} = \dfrac{p(z)\,b(z)}{a^*(z)}$",
            fontsize=13, ha="center", va="center", color=NAVY)
    ax.text(6.88, 2.75, "• Equação Diofantina:  a(z)ℓ(z) + b(z)p(z) = a*(z)", fontsize=12, color=TXT)
    ax.text(6.88, 2.25, "• Modelo Interno (degrau): s = 0 ⇒ z = e⁰ = 1 ⇒ ℓ(z) = (z − 1)ℓ₂(z)",
            fontsize=11.5, color=GREEN, weight="bold")
    ax.text(6.88, 1.7, "• Regra do trabalho: Δt = τ_min/100 = 0,5 ms  |  h = τ_min/10 = 5 ms",
            fontsize=11, color=NAVY)
    return fig


def s_discretizacao_zoh(d, num, total):
    fig, ax = novo_slide("Discretização Exata da Planta via ZOH (h = 0,005 s)", num, total, etapa=3,
                         resumo="usando a Equivalência do ZOH (Aula 08), convertemos G(s) para G(z) sem aproximações")

    caixa(ax, 0.6, 1.28, 12.13, 4.35, fc=LIGHT)

    ax.text(0.9, 5.25, "1. Fórmula da Equivalência do ZOH (Aula 08):", fontsize=13, weight="bold", color=NAVY)
    ax.text(7.2, 5.25, r"$G(z) = \dfrac{z-1}{z}\,\mathcal{Z}\left\{\mathcal{L}^{-1}\left[\dfrac{G(s)}{s}\right]_{t=kh}\right\}$",
            fontsize=14.5, va="center", color=ACC)

    ax.text(0.9, 4.55, "2. Frações Parciais de G(s)/s:", fontsize=13, weight="bold", color=NAVY)
    ax.text(1.2, 3.98, r"$\dfrac{G(s)}{s} = \dfrac{533{,}33}{s(s+20)(s+6{,}67)} = \dfrac{A}{s} + \dfrac{B}{s+20} + \dfrac{C}{s+6{,}67} = \dfrac{4}{s} + \dfrac{2}{s+20} - \dfrac{6}{s+6{,}67}$",
            fontsize=13, color=TXT)

    ax.text(0.9, 3.3, "3. Transformada Inversa de Laplace e Amostragem (t = kh, h = 0,005 s):",
            fontsize=13, weight="bold", color=NAVY)
    ax.text(1.2, 2.82, r"$y_u(kh) = 4 + 2e^{-20kh} - 6e^{-6{,}67kh} \quad \text{com } z_1 = e^{-20h} = 0{,}904837,\;\; z_2 = e^{-6{,}67h} = 0{,}967216$",
            fontsize=12.5, color=TXT)

    ax.text(0.9, 2.28, "4. Transformada Z e Multiplicação por (z − 1)/z:", fontsize=13, weight="bold", color=NAVY)
    ax.text(1.2, 1.72, r"$G(z) = 4 + \dfrac{2(z-1)}{z-0{,}904837} - \dfrac{6(z-1)}{z-0{,}967216} = \dfrac{b(z)}{a(z)} = \dfrac{0{,}006378\,z + 0{,}006101}{z^2 - 1{,}872054\,z + 0{,}875173}$",
            fontsize=13.5, color=NAVY)
    return fig


def s_diofantina(num, total):
    fig, ax = novo_slide("Método Polinomial: Equação Diofantina Passo a Passo", num, total, etapa=3,
                         resumo="com ã(z) de grau 3 e a*(z) de grau 4, o sistema linear 4×4 tem solução única e causal")

    # Esquerda: Coprimalidade, Graus e a*(z)
    caixa(ax, 0.6, 1.28, 5.75, 4.35, fc=LIGHT)
    ax.text(0.85, 5.28, "1. Coprimalidade e Graus (Teorema Aula 10)", fontsize=13, weight="bold", color=NAVY)
    ax.text(0.85, 4.82, "• Polos a(z): {0,9048; 0,9672}  ≠  Zero b(z): −0,9565 → coprimos", fontsize=10.8, color=TXT)
    ax.text(0.85, 4.38, "• Modelo Interno: $\\tilde{a}(z) = a(z)(z-1)$", fontsize=10.3, color=NAVY)
    ax.text(1.05, 4.08, r"$= z^3 - 2{,}872054\,z^2 + 2{,}747227\,z - 0{,}875173$", fontsize=10.0, color=NAVY)
    ax.text(0.85, 3.66, r"• $n_{\tilde{a}} = 3,\; n_b = 1$. Com $n_{a^*} = 4 > 3 \;\Rightarrow\; n_p < 3,\; n_{\ell_2} \leq 1$:",
            fontsize=10.2, color=TXT)
    ax.text(0.85, 3.25, r"$\ell_2(z) = z + \ell_{20}, \qquad p(z) = p_2 z^2 + p_1 z + p_0$", fontsize=11.5, color=ACC)

    ax.text(0.85, 2.75, r"2. Polinômio Desejado $a^*(z)$ ($z = e^{sh}$)", fontsize=12.5, weight="bold", color=NAVY)
    ax.text(0.85, 2.32, "Polos em s = {−10, −10, −25, −25} → z = {0,951229 (×2); 0,882497 (×2)}",
            fontsize=10.0, color=TXT)
    ax.text(0.85, 1.78, r"$a^*(z) = (z - 0{,}951229)^2(z - 0{,}882497)^2$" "\n"
                        r"$= z^4 - 3{,}667453z^3 + 5{,}041466z^2 - 3{,}078669z + 0{,}704688$",
            fontsize=10.0, color=NAVY, va="center", linespacing=1.4)

    # Direita: Sistema 4x4 explícito e solução
    caixa(ax, 6.55, 1.28, 6.18, 4.35, fc=ACC_LIGHT, ec=ACC, lw=1.6)
    ax.text(6.8, 5.28, "3. Igualando os Coeficientes de ã(z)(z + ℓ₂₀) + b(z)p(z) = a*(z)",
            fontsize=12, weight="bold", color=NAVY)

    eqs = [
        r"$z^3:\; -2{,}872054 + \ell_{20} + 0{,}006378\,p_2 = -3{,}667453$",
        r"$z^2:\; 2{,}747227 - 2{,}872054\,\ell_{20} + 0{,}006101\,p_2 + 0{,}006378\,p_1 = 5{,}041466$",
        r"$z^1:\; -0{,}875173 + 2{,}747227\,\ell_{20} + 0{,}006101\,p_1 + 0{,}006378\,p_0 = -3{,}078669$",
        r"$z^0:\; -0{,}875173\,\ell_{20} + 0{,}006101\,p_0 = 0{,}704688$",
    ]
    yy = 4.72
    for eq in eqs:
        ax.text(6.8, yy, eq, fontsize=10.3, color=TXT)
        yy -= 0.45

    ax.text(6.8, 2.85, "4. Solução Única do Sistema 4×4:", fontsize=12.5, weight="bold", color=GREEN)
    ax.text(6.8, 2.4, r"$\ell_{20} = -0{,}800410 \;\Rightarrow\; \ell(z) = (z-1)(z-0{,}800410) = z^2 - 1{,}800410z + 0{,}800410$",
            fontsize=10.2, color=TXT)
    ax.text(6.8, 1.98, r"$p_2 = 0{,}785669,\quad p_1 = -1{,}469869,\quad p_0 = 0{,}686831$",
            fontsize=10.8, color=TXT)
    ax.text(9.64, 1.52, r"$C(z) = \dfrac{0{,}785669\,z^2 - 1{,}469869\,z + 0{,}686831}{z^2 - 1{,}800410\,z + 0{,}800410}$",
            fontsize=12.5, ha="center", va="center", color=NAVY)
    return fig


def s_algoritmo(d, num, total):
    fig, ax = novo_slide("Algoritmo do Controlador (Conversão para z⁻¹ → u(k))", num, total, etapa=3,
                         resumo="dividindo C(z) por z² obtemos a equação a diferenças causal executada a cada h = 5 ms (ZOH)")

    # Esquerda: dedução da equação a diferenças + código
    caixa(ax, 0.6, 3.82, 7.1, 1.82, fc=ACC_LIGHT, ec=ACC, lw=1.4)
    ax.text(0.85, 5.36, "Passagem para Equação a Diferenças (dividindo por z²):", fontsize=12, weight="bold", color=NAVY)
    ax.text(0.85, 4.86, r"$\dfrac{U(z)}{E(z)} = \dfrac{0{,}785669 - 1{,}469869\,z^{-1} + 0{,}686831\,z^{-2}}{1 - 1{,}800410\,z^{-1} + 0{,}800410\,z^{-2}}$",
            fontsize=11.0, color=TXT)
    ax.text(0.85, 4.30, r"$u(k) = 1{,}800410\,u(k-1) - 0{,}800410\,u(k-2)$", fontsize=10.5, color=NAVY)
    ax.text(1.42, 3.98, r"$+\;0{,}785669\,e(k) - 1{,}469869\,e(k-1) + 0{,}686831\,e(k-2)$", fontsize=10.5, color=NAVY)

    caixa(ax, 0.6, 1.28, 7.1, 2.38, fc="#1C222B", r=0.12)
    codigo = (
        "// Parametros: h=0.005s, ell1=-1.800410, ell0=0.800410\n"
        "//             p2=0.785669, p1=-1.469869, p0=0.686831\n"
        "while (loop) {              // a cada h = tau_min/10 = 5 ms\n"
        "   y = vin1();   e = r - y;\n"
        "   u = -ell1*u1 - ell0*u2 + p2*e + p1*e1 + p0*e2;\n"
        "   u2 = u1; u1 = u;  e2 = e1; e1 = e;\n"
        "   vout1(u);                // mantem por 10 iteracoes dt (ZOH)\n"
        "}"
    )
    ax.text(0.85, 3.44, codigo, family="DejaVu Sans Mono", fontsize=10.6, color="#E6EDF3", va="top",
            linespacing=1.4)

    # Direita: ZOH
    caixa(ax, 7.95, 1.28, 4.78, 4.35, fc=LIGHT)
    ax.text(8.2, 5.25, "Princípio do ZOH (10 passos Δt por amostra h)", fontsize=12, weight="bold", color=NAVY)
    tc, rc, yc, uc = d["cc"]
    ap = eixo(fig, 8.6, 2.52, 3.88, 2.32)
    m = tc <= 0.0401
    ap.plot(tc[m], uc[m], drawstyle="steps-post", color=RED, lw=2)
    ap.plot(tc[m], uc[m], ".", color=NAVY, ms=2.5)
    ap.set_xticks([0, 0.01, 0.02, 0.03, 0.04])
    ap.set_xticklabels(["0", "10", "20", "30", "40"])
    ap.set_xlabel("tempo [ms]", fontsize=10.5)
    ap.set_ylabel("u(t) [V]", fontsize=10.5)
    ap.tick_params(labelsize=9.5)
    ap.grid(True, color="#E3E8EE", lw=0.8)
    ax.text(8.2, 1.62, "Cada patamar de u(t) dura h = 5 ms\n(10 iterações RK4 de Δt = 0,5 ms).",
            fontsize=10.6, color=GRAY, va="center", linespacing=1.3)
    return fig


def s_com_controlador(d, num, total):
    fig, ax = novo_slide("Simulação em Malha Fechada COM Controlador", num, total, etapa=4,
                         resumo="erro zerado (0%), P.O. caiu de 15,24% para 0,88%, Ts caiu para 0,2565 s e u ∈ [0,75; 2,36] V")
    ts, rs, ysc, usc = d["sc"]
    tc, rc, ycc, ucc = d["cc"]
    msc, mcc = d["m_sc"], d["m_cc"]

    ax.text(0.6, 5.45, "Comparação direta para o mesmo degrau r = 3,0 V (300 lux):", fontsize=12.5, color=GRAY)
    ay, au = grafico_resposta(
        fig, 1.25, 1.32, 6.9, 3.85,
        [(ts, rs, dict(color="black", ls="--", lw=1.6, label="referência")),
         (ts, ysc, dict(color="#AAB4BF", lw=2.0, label="sem controlador")),
         (tc, ycc, dict(color=ACC, lw=2.8, label="com controlador"))],
        [(ts, usc, dict(color="#AAB4BF", lw=1.6)), (tc, ucc, dict(color=RED, lw=2.0))])
    ay.legend(loc="lower right", frameon=False, fontsize=10.5)

    x0, y0, w0, h0 = 8.55, 1.32, 4.18, 4.3
    caixa(ax, x0, y0, w0, h0, fc=LIGHT)
    cx = [x0 + 0.2, x0 + 1.95, x0 + 2.95, x0 + 4.0]
    yy = y0 + h0 - 0.35
    for c, txt, ha in zip(cx, ["", "Sem", "Com", "Meta"], ["left", "center", "center", "right"]):
        ax.text(c, yy, txt, fontsize=12.5, weight="bold", color=GRAY, ha=ha, va="center")
    linhas = [
        ("Erro em\nregime", f"{msc['ess_pct']:.0f} %", "≈ 0 %", "0 %"),
        ("Overshoot", f"{br(msc['po_regime_pct'], 1)} %", f"{br(mcc['po_ref_pct'], 2)} %", "≤ 5 %"),
        ("Ts (2%)", f"{br(msc['ts_2'], 4)} s", f"{br(mcc['ts_2'], 4)} s", "≤ 0,30 s"),
        ("u máximo", f"{br(np.max(usc), 2)} V", f"{br(np.max(ucc), 2)} V", "≤ 5 V"),
    ]
    yy -= 0.72
    for i, (lab, s, c, meta) in enumerate(linhas):
        ax.text(cx[0], yy, lab, fontsize=11.5, color=TXT, va="center", linespacing=1.1)
        ax.text(cx[1], yy, s, fontsize=12, color=RED if lab != "u máximo" else GRAY, ha="center", va="center")
        ax.text(cx[2], yy, c, fontsize=12.5, color=GREEN, weight="bold", ha="center", va="center")
        ax.text(cx[3], yy, meta, fontsize=11, color=GRAY, ha="right", va="center")
        if i < len(linhas) - 1:
            ax.plot([x0 + 0.2, x0 + w0 - 0.2], [yy - 0.37, yy - 0.37], color="#DDE3EA", lw=1)
        yy -= 0.74
    caixa(ax, x0 + 0.2, y0 + 0.16, w0 - 0.4, 0.54, fc=GREEN, r=0.26)
    ax.text(x0 + w0 / 2, y0 + 0.43, "4 de 4 metas atendidas", fontsize=13.5, weight="bold",
            color="white", ha="center", va="center")
    return fig


def s_ajuste(d, num, total):
    fig, ax = novo_slide("Ajuste Fino da Sintonia (1ª Tentativa vs. Final)", num, total, etapa=4,
                         resumo="polos muito rápidos amplificam os zeros de p(z) e saturam o driver  →  ajuste para −10 e −25")
    t1, r1, y1, u1 = d["t1"]
    tc, rc, yc, uc = d["cc"]
    m1, mc = d["m_t1"], d["m_cc"]

    ay, au = grafico_resposta(
        fig, 1.25, 1.32, 6.9, 4.1,
        [(t1, r1, dict(color="black", ls="--", lw=1.6, label="referência")),
         (t1, y1, dict(color=ORANGE, lw=2.2, label="1ª tentativa (−18, −30)")),
         (tc, yc, dict(color=ACC, lw=2.6, label="final (−10, −25)"))],
        [(t1, u1, dict(color=ORANGE, lw=1.8)), (tc, uc, dict(color=RED, lw=2.0))],
        ylim_y=(0, 3.5), ylim_u=(-0.3, 7.9))
    ay.legend(loc="lower right", frameon=False, fontsize=10.5)

    caixa(ax, 8.55, 3.55, 4.18, 2.0, fc=ORANGE_LIGHT)
    ax.text(8.8, 5.18, "1ª tentativa: polos −18 e −30", fontsize=13, weight="bold", color="#9C640C")
    ax.text(8.8, 4.7, f"• P.O. = {br(m1['po_ref_pct'], 2)} % (> 5 %)\n"
                      f"• u_max = {br(np.max(u1), 2)} V (> 5,0 V)",
            fontsize=12, color=RED, va="top", linespacing=1.55)

    caixa(ax, 8.55, 1.32, 4.18, 2.0, fc=GREEN_LIGHT)
    ax.text(8.8, 2.95, "Final: polos −10 e −25", fontsize=13, weight="bold", color=GREEN)
    ax.text(8.8, 2.48, f"• P.O. = {br(mc['po_ref_pct'], 2)} % (<= 5 %)\n"
                       f"• u_max = {br(np.max(uc), 2)} V (<= 5,0 V)\n"
                       f"• Ts(2%) = {br(mc['ts_2'], 4)} s (<= 0,30 s)",
            fontsize=12, color=TXT, va="top", linespacing=1.45)
    return fig


def s_conclusao(num, total):
    fig, ax = novo_slide("Conclusões", num, total, etapa=None,
                         resumo="o Método Polinomial com modelo interno atendeu às 4 metas com algoritmo leve (5 mult. + 4 somas)")
    itens = [
        ("Planta", "LED + LDR modelados como 2ª ordem estável (Tipo 0), com Δt = 0,5 ms e h = 5 ms."),
        ("Sem controlador", "Cálculo analítico e simulação concordaram: e_ss = 20% e P.O. ≈ 15%."),
        ("Projeto Polinomial", "Equação Diofantina + modelo interno (z − 1) zerou o erro em regime."),
        ("Com controlador", "Ajuste fino levou P.O. para 0,88%, Ts para 0,2565 s e u ∈ [0,75; 2,36] V."),
    ]
    yy = 5.22
    for i, (tit, txt) in enumerate(itens, 1):
        ax.add_patch(Circle((0.95, yy - 0.12), 0.25, color=ACC))
        ax.text(0.95, yy - 0.12, str(i), ha="center", va="center", fontsize=13, weight="bold", color="white")
        ax.text(1.4, yy, tit, fontsize=14.5, weight="bold", color=NAVY, va="center")
        ax.text(1.4, yy - 0.3, txt, fontsize=12, color=TXT, va="top")
        yy -= 0.96

    caixa(ax, 8.1, 1.32, 4.63, 4.3, fc=NAVY, r=0.18)
    ax.text(10.42, 5.22, "Simulador + Slides Online", ha="center", fontsize=14.5, weight="bold", color="white")
    caixa(ax, 9.27, 2.38, 2.3, 2.4, fc="white", r=0.1)
    ax_qr = eixo(fig, 9.37, 2.48, 2.1, 2.2)
    ax_qr.imshow(qr_image(URL_SIMULADOR), interpolation="nearest")
    ax_qr.axis("off")
    ax.text(10.42, 2.0, URL_SIMULADOR.replace("https://", ""), ha="center", fontsize=9.3, color="#D2E2F4")
    ax.text(10.42, 1.6, "Obrigado!  Perguntas?", ha="center", fontsize=13, weight="bold", color=YELLOW)
    return fig


# ------------------------------------------------------------------------------
# Roteiro (~9 min 30 s)
# ------------------------------------------------------------------------------
ROTEIRO = [
    ("Capa", "20 s",
     "Meu trabalho é o controle digital de iluminação adaptativa: manter uma bancada em 300 lux "
     "usando driver LED, sensor LDR e controlador projetado pelo Método Polinomial. O QR code abre o simulador online."),
    ("A planta", "45 s",
     "A planta é uma luminária LED sobre uma bancada. A entrada u é a tensão no driver, de 0 a 5 V, e a saída y é a tensão "
     "do sensor LDR calibrada para 1 V igual a 100 lux. O objetivo é manter a luz exatamente no valor desejado."),
    ("Modelagem", "1 min",
     "Modelando cada bloco por uma equação diferencial de 1ª ordem e aplicando Laplace, temos 400/(0,05s+1) para o LED e "
     "0,01/(0,15s+1) para o LDR. Multiplicando, chegamos a G(s) = 4 / [(0,05s+1)(0,15s+1)], de 2ª ordem, Tipo 0, com polos em "
     "-20 e -6,67 rad/s. Também escrevo em variáveis de estado para integrar por RK4."),
    ("Análise em Malha Fechada sem Controlador", "50 s",
     "Fechando a malha sem controlador (C(s)=1), calculamos G_MF(s) = 533,33 / (s² + 26,67s + 666,67). "
     "Daí tiramos wn = 25,82 rad/s e zeta = 0,5164, prevendo overshoot de 15%. Pelo Teorema do Valor Final, "
     "y(infinito) = 2,40 V para degrau de 3 V, logo erro de regime de 20%."),
    ("Simulação sem Controlador", "45 s",
     "Integrando a planta com passo Δt = τ_min/100 = 0,5 ms, a simulação confirma exatamente as contas: "
     "erro de 20% (para em 2,40 V), overshoot de 15,24% e acomodação em 0,31 s."),
    ("Especificações e Método", "45 s",
     "Defini quatro metas: erro zero, P.O. <= 5%, Ts <= 0,30 s e u entre 0 e 5 V. Escolhi a Segunda Maneira com o "
     "Método Polinomial da Aula 10: resolver a Equação Diofantina a(z)ℓ(z) + b(z)p(z) = a*(z) com modelo interno (z-1)."),
    ("Discretização ZOH", "1 min",
     "Seguindo a Aula 08, aplicamos a Equivalência do ZOH para h = τ_min/10 = 5 ms. Expandindo G(s)/s em frações parciais, "
     "encontramos A=4, B=2 e C=-6. Aplicando a Transformada Z e multiplicando por (z-1)/z, obtemos G(z) exata."),
    ("Equação Diofantina", "1 min 15 s",
     "Verificamos que a(z) e b(z) são coprimos. Impondo ℓ(z)=(z-1)ℓ₂(z), ã(z) fica de grau 3, então com a*(z) de grau 4 "
     "temos solução única causal com ℓ₂ de grau 1 e p de grau 2. Mapeando os polos -10 e -25 para z, montamos o sistema 4x4 "
     "igualando potências de z e chegamos ao controlador C(z)."),
    ("Algoritmo e ZOH", "45 s",
     "Dividindo numerador e denominador de C(z) por z² e aplicando Z inversa, temos a equação a diferenças causal. "
     "No algoritmo, a cada 5 ms lê y, calcula e = r - y, calcula u e mantém constante por 10 passos Δt pelo princípio do ZOH."),
    ("Simulação com Controlador", "50 s",
     "Comparando com a curva sem controlador: erro caiu de 20% para zero, overshoot de 15,24% para 0,88%, Ts para 0,2565 s "
     "e controle entre 0,75 e 2,36 V. Todas as 4 metas foram atendidas."),
    ("Ajuste Fino", "35 s",
     "Mostrando o ajuste fino: na 1ª tentativa com polos em -18 e -30, os zeros de p(z) causaram overshoot de 8,79% e pico "
     "de u em 7,23 V (acima de 5 V). Suavizando os polos para -10 e -25, todas as especificações ficaram dentro da meta."),
    ("Conclusões", "30 s",
     "Concluindo: a análise teórica e a simulação bateram perfeitamente, o Método Polinomial zerou o erro e atendeu todas "
     "as metas com um algoritmo leve. O simulador completo está online no QR code. Obrigado!"),
]


def salvar_roteiro():
    linhas = ["# Roteiro da apresentação (≈ 9 min 30 s)\n\n",
              f"Simulador online: {URL_SIMULADOR}\n"]
    for i, (tit, tempo, fala) in enumerate(ROTEIRO, 1):
        linhas.append(f"\n## Slide {i} — {tit} ({tempo})\n\n{fala}\n")
    with open(os.path.join(OUT_DIR, "roteiro_apresentacao.md"), "w", encoding="utf-8") as f:
        f.write("".join(linhas))


def salvar_pptx(pngs):
    try:
        from pptx import Presentation
        from pptx.util import Inches
    except ImportError:
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
    for f in os.listdir(SLIDES_DIR):
        os.remove(os.path.join(SLIDES_DIR, f))
    d = calcular_dados()
    construtores = [
        lambda n, T: s_capa(),
        lambda n, T: s_planta(n, T),
        lambda n, T: s_modelagem(n, T),
        lambda n, T: s_analise_mf_sem_ctrl(n, T),
        lambda n, T: s_sem_controlador(d, n, T),
        lambda n, T: s_especificacoes(n, T),
        lambda n, T: s_discretizacao_zoh(d, n, T),
        lambda n, T: s_diofantina(n, T),
        lambda n, T: s_algoritmo(d, n, T),
        lambda n, T: s_com_controlador(d, n, T),
        lambda n, T: s_ajuste(d, n, T),
        lambda n, T: s_conclusao(n, T),
    ]
    total = len(construtores)
    assert total == len(ROTEIRO)
    pngs = []
    with PdfPages(os.path.join(OUT_DIR, "apresentacao_controle_iluminacao.pdf")) as pdf:
        for i, cons in enumerate(construtores, 1):
            fig = cons(i, total)
            png = os.path.join(SLIDES_DIR, f"slide_{i:02d}.png")
            fig.savefig(png, dpi=150)
            pdf.savefig(fig)
            plt.close(fig)
            pngs.append(png)
    salvar_pptx(pngs)
    salvar_roteiro()
    print(f"{total} slides gerados em ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
