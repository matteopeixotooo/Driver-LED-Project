"""
Gera a apresentação (16:9, ~10 min) do trabalho de Controle Digital — Controle de Iluminação.

Segue o roteiro pedido pelo professor:
  1) a planta  ->  equações  ->  função de transferência / variáveis de estado
  2) malha fechada sem controlador e seus problemas
  3) especificações, tipo de controlador e método de projeto
  4) malha fechada com controlador e comparação com as especificações

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
# Configuração (edite aqui)
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
    """Número com vírgula decimal."""
    return f"{v:.{dec}f}".replace(".", ",")


# ------------------------------------------------------------------------------
# Helpers de desenho (polegadas, origem no canto inferior esquerdo)
# ------------------------------------------------------------------------------
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
    """Slide padrão: título, trilha das 4 etapas do professor, faixa de resumo e rodapé."""
    fig = plt.figure(figsize=(W, HH))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, HH)
    ax.axis("off")

    # Trilha de progresso (as 4 etapas pedidas pelo professor)
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

    ax.text(0.6, 6.25, titulo, fontsize=27, weight="bold", color=NAVY, va="center")
    ax.plot([0.62, 1.7], [5.82, 5.82], color=ACC, lw=4, solid_capstyle="round")

    if resumo:
        caixa(ax, 0.6, 0.5, 12.13, 0.62, fc=ACC_LIGHT, r=0.12)
        ax.add_patch(Rectangle((0.6, 0.5), 0.09, 0.62, color=ACC))
        ax.text(0.9, 0.81, "Resumo:", fontsize=13.5, weight="bold", color=NAVY, va="center")
        ax.text(2.0, 0.81, resumo, fontsize=13.5, color=TXT, va="center")

    ax.text(0.6, 0.18, f"{NOME}  ·  Controle Digital 2026/2  ·  Controle Digital de Iluminação",
            fontsize=9.5, color=GRAY)
    ax.text(W - 0.6, 0.18, f"{num} / {total}", fontsize=9.5, color=GRAY, ha="right")
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
    """Gráfico padrão exigido no trabalho: (cima) referência + saída, (baixo) entrada da planta."""
    h_u = h * 0.34
    h_y = h - h_u - 0.3
    ay = eixo(fig, x, y + h_u + 0.3, w, h_y)
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


# ------------------------------------------------------------------------------
# Dados das simulações (mesmo modelo de simulacao_iluminacao.py)
# ------------------------------------------------------------------------------
def simular_malha_aberta(u_val, t_total):
    n = int(round(t_total / sim.DT))
    t = np.arange(n) * sim.DT
    y = np.zeros(n)
    x1 = x2 = 0.0
    for i in range(n):
        y[i] = x1
        x1, x2 = sim.passo_rk4_planta(x1, x2, u_val, sim.DT)
    return t, np.full(n, u_val), y


def calcular_dados():
    b, a, _, _ = sim.discretizar_planta_zoh(sim.TAU_1, sim.TAU_2, sim.K_PLANTA, sim.H)
    ell_f, p_f, _, _ = sim.projetar_controlador_polinomial(b, a, [-10, -10, -25, -25], sim.H)
    ell_1, p_1, _, _ = sim.projetar_controlador_polinomial(b, a, [-18, -18, -30, -30], sim.H)

    r = 3.0
    d = {"b": b, "a": a, "ell": ell_f, "p": p_f}
    d["ma"] = simular_malha_aberta(0.75, 1.0)
    d["sc"] = sim.simular_sem_controlador(lambda t: r, 1.0)
    d["cc"] = sim.simular_com_controlador(lambda t: r, 1.0, ell_f, p_f)
    d["t1"] = sim.simular_com_controlador(lambda t: r, 1.0, ell_1, p_1)

    d["m_ma"] = sim.calcular_metricas_degrau(d["ma"][0], d["ma"][2], 3.0)
    d["m_sc"] = sim.calcular_metricas_degrau(d["sc"][0], d["sc"][2], r)
    d["m_cc"] = sim.calcular_metricas_degrau(d["cc"][0], d["cc"][2], r)
    d["m_t1"] = sim.calcular_metricas_degrau(d["t1"][0], d["t1"][2], r)
    return d


# ------------------------------------------------------------------------------
# Slides
# ------------------------------------------------------------------------------
def s_capa(total):
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
                       "um LED, um sensor LDR e um controlador digital",
            fontsize=18, color="#D2E2F4", va="center", linespacing=1.35)
    ax.plot([0.92, 2.2], [1.95, 1.95], color=YELLOW, lw=4, solid_capstyle="round")
    ax.text(0.9, 1.4, NOME, fontsize=18, color="white", weight="bold")

    # QR do simulador
    caixa(ax, 9.25, 1.55, 3.3, 4.35, fc="white", r=0.2)
    ax_qr = eixo(fig, 9.6, 2.45, 2.6, 2.6)
    ax_qr.imshow(qr_image(URL_SIMULADOR), interpolation="nearest")
    ax_qr.axis("off")
    ax.text(10.9, 5.45, "Simulador online", ha="center", fontsize=15, weight="bold", color=NAVY)
    ax.text(10.9, 2.05, URL_SIMULADOR.replace("https://", ""), ha="center", fontsize=9,
            color=GRAY, wrap=True)
    return fig


def s_planta(num, total):
    fig, ax = novo_slide("A planta: uma luminária que se ajusta sozinha", num, total, etapa=1,
                         resumo="entrada u = tensão no driver do LED (0 a 5 V)  ·  saída y = tensão do sensor (1 V = 100 lux)")

    # --- Ilustração ---
    caixa(ax, 0.6, 1.35, 6.4, 4.3, fc="#FAFBFD", ec="#E1E6ED", lw=1.2)
    # luz
    ax.add_patch(Polygon([(2.15, 4.62), (3.35, 4.62), (4.55, 2.05), (0.95, 2.05)],
                         closed=True, fc=YELLOW, alpha=0.22, lw=0))
    ax.text(2.75, 3.1, "300 lux", ha="center", fontsize=17, weight="bold", color="#9A7300")
    # luminária
    ax.plot([2.75, 2.75], [5.0, 5.55], color=NAVY, lw=2)
    ax.add_patch(Polygon([(2.1, 4.65), (3.4, 4.65), (3.05, 5.02), (2.45, 5.02)],
                         closed=True, fc=NAVY, lw=0))
    ax.add_patch(Rectangle((2.2, 4.58), 1.1, 0.08, color=YELLOW))
    ax.text(1.95, 4.9, "LED", ha="right", fontsize=13, weight="bold", color=NAVY)
    # bancada
    ax.add_patch(Rectangle((0.9, 1.85), 4.6, 0.2, color="#8D9AA8"))
    ax.add_patch(Rectangle((1.1, 1.45), 0.12, 0.4, color="#8D9AA8"))
    ax.add_patch(Rectangle((5.18, 1.45), 0.12, 0.4, color="#8D9AA8"))
    ax.text(1.6, 1.6, "bancada", fontsize=11, color=GRAY)
    # sensor
    ax.add_patch(Circle((4.1, 2.17), 0.12, color=RED, zorder=4))
    ax.text(4.1, 2.45, "sensor LDR", ha="center", fontsize=11.5, weight="bold", color=RED)
    # computador
    bloco(ax, 5.25, 3.45, 1.55, 0.95, "Controlador", "computador", fc=ACC_LIGHT, ec=ACC, tsize=12.5)
    ax.plot([4.25, 6.02, 6.02], [2.17, 2.17, 3.45], color=ACC, lw=2.2, ls="--")
    seta(ax, 6.02, 3.0, 6.02, 3.42, cor=ACC, lw=2.2, ms=16)
    ax.text(6.15, 2.6, "mede y", fontsize=11, color=ACC, weight="bold")
    ax.plot([5.25, 3.6], [4.15, 4.83], color=RED, lw=2.2)
    seta(ax, 3.9, 4.71, 3.45, 4.88, cor=RED, lw=2.2, ms=16)
    ax.text(4.55, 4.75, "ajusta u", fontsize=11, color=RED, weight="bold", rotation=-22)

    # --- Texto explicativo ---
    xt = 7.35
    itens = [
        ("O problema", "Manter a iluminação de uma bancada (laboratório,\nescritório, estufa) num valor desejado, ex.: 300 lux."),
        ("Como funciona", "Um sensor de luz (LDR) mede a iluminação e um\ncomputador ajusta a tensão aplicada no LED."),
        ("Por que controlar?", "Sem controle a luz não chega no valor pedido\ne pode oscilar quando muda o nível desejado."),
    ]
    yy = 5.35
    for tit, txt in itens:
        ax.text(xt, yy, tit, fontsize=16, weight="bold", color=NAVY, va="center")
        ax.text(xt, yy - 0.42, txt, fontsize=13, color=TXT, va="top", linespacing=1.4)
        yy -= 1.38
    return fig


def s_componentes(d, num, total):
    fig, ax = novo_slide("Como cada parte da planta se comporta", num, total, etapa=1,
                         resumo="dois blocos de 1ª ordem em série (τ₁ = 0,05 s e τ₂ = 0,15 s)  →  planta de 2ª ordem")

    # Diagrama em linha
    yb, hb = 4.35, 1.2
    ax.text(0.85, yb + hb / 2, "u(t)", ha="center", va="center", fontsize=18, weight="bold", color=RED)
    seta(ax, 1.15, yb + hb / 2, 1.42, yb + hb / 2, ms=16)
    bloco(ax, 1.45, yb, 3.1, hb, "Driver de LED", "tensão → luz", tsize=15)
    seta(ax, 4.55, yb + hb / 2, 5.2, yb + hb / 2)
    ax.text(4.87, yb + hb / 2 + 0.22, "luz Φ", ha="center", fontsize=11, color=GRAY)
    bloco(ax, 5.25, yb, 3.1, hb, "Sensor LDR", "luz → tensão", tsize=15)
    seta(ax, 8.35, yb + hb / 2, 8.62, yb + hb / 2, ms=16)
    ax.text(8.9, yb + hb / 2, "y(t)", ha="center", va="center", fontsize=18, weight="bold", color=ACC)

    # Cartões dos componentes
    cards = [
        (1.45, "Driver de LED", [("τ₁ = 0,05 s", "filtro RC que suaviza o PWM do LED"),
                                 ("K = 400 lux/V", "cada volt gera 400 lux")]),
        (5.25, "Sensor LDR + filtro", [("τ₂ = 0,15 s", "inércia do LDR + filtro anti-ruído 60 Hz"),
                                       ("K = 0,01 V/lux", "100 lux geram 1 V")]),
    ]
    for x, tit, linhas in cards:
        caixa(ax, x, 1.45, 3.1, 2.6, fc=LIGHT)
        ax.text(x + 0.22, 3.68, tit, fontsize=14, weight="bold", color=NAVY)
        yy = 3.12
        for big, small in linhas:
            ax.text(x + 0.22, yy, big, fontsize=15, weight="bold", color=ACC)
            ax.text(x + 0.22, yy - 0.36, small, fontsize=10.8, color=GRAY)
            yy -= 0.92

    # O que é tau?
    caixa(ax, 9.25, 1.45, 3.48, 4.1, fc=ORANGE_LIGHT)
    ax.text(9.45, 5.15, "O que é τ (constante de tempo)?", fontsize=12.5, weight="bold", color="#9C640C")
    ap = eixo(fig, 9.75, 2.55, 2.75, 2.15)
    tt = np.linspace(0, 5, 300)
    ap.plot(tt, 1 - np.exp(-tt), color=ORANGE, lw=2.5)
    ap.axhline(1, color=GRAY, ls="--", lw=1)
    ap.plot([1, 1, 0], [0, 0.632, 0.632], color=NAVY, ls=":", lw=1.4)
    ap.plot(1, 0.632, "o", color=NAVY)
    ap.text(1.15, 0.5, "63 % em t = τ", fontsize=10.5, color=NAVY, weight="bold")
    ap.set_xticks([0, 1, 2, 3, 4, 5])
    ap.set_xticklabels(["0", "τ", "2τ", "3τ", "4τ", "5τ"])
    ap.set_yticks([0, 0.5, 1])
    ap.set_ylim(0, 1.12)
    ap.set_xlim(0, 5)
    ap.grid(True, color="#F0E0C8", lw=0.8)
    ax.text(9.45, 1.95, "É o \"tempo de reação\" do bloco:\nquanto maior τ, mais lento.",
            fontsize=11, color=TXT, va="center", linespacing=1.35)
    return fig


def s_modelagem(num, total):
    fig, ax = novo_slide("Modelagem: das equações ao modelo", num, total, etapa=1,
                         resumo="G(s) = 4 / [(0,05s + 1)(0,15s + 1)]  —  é este modelo que é simulado e usado no projeto")

    y0, h0 = 1.45, 4.05
    cols = [(0.6, 3.8, "① Equações diferenciais"), (4.75, 3.95, "② Função de transferência"),
            (9.05, 3.68, "③ Variáveis de estado")]
    for i, (x, w, tit) in enumerate(cols):
        destaque = (i == 1)
        caixa(ax, x, y0, w, h0, fc=ACC_LIGHT if destaque else LIGHT,
              ec=ACC if destaque else "none", lw=2)
        ax.text(x + 0.25, y0 + h0 - 0.42, tit, fontsize=15, weight="bold", color=NAVY)
    seta(ax, 4.43, y0 + h0 / 2, 4.7, y0 + h0 / 2, ms=18)
    seta(ax, 8.73, y0 + h0 / 2, 9.0, y0 + h0 / 2, ms=18)

    # 1
    x = 0.85
    ax.text(x, 4.65, "Driver de LED:", fontsize=12, color=GRAY)
    ax.text(x, 4.15, r"$\tau_1\,\dot{\Phi}+\Phi=K_{LED}\,u$", fontsize=18, color=TXT)
    ax.text(x, 3.45, "Sensor LDR:", fontsize=12, color=GRAY)
    ax.text(x, 2.95, r"$\tau_2\,\dot{y}+y=K_{LDR}\,\Phi$", fontsize=18, color=TXT)
    ax.text(x, 2.05, "cada bloco é um sistema\nde 1ª ordem (atraso simples)", fontsize=11.5,
            color=GRAY, va="center", linespacing=1.35)

    # 2
    xc = 4.75 + 3.95 / 2
    ax.text(4.98, 4.6, "Laplace e multiplicando os blocos:", fontsize=11.5, color=GRAY)
    ax.text(xc, 3.75, r"$G(s)=\dfrac{Y(s)}{U(s)}=\dfrac{4}{(0{,}05s+1)(0{,}15s+1)}$",
            fontsize=15.5, ha="center", va="center", color=NAVY)
    ax.text(xc, 2.55, r"$=\dfrac{533{,}3}{s^2+26{,}7\,s+133{,}3}$",
            fontsize=16, ha="center", va="center", color=TXT)
    ax.text(4.98, 1.75, "ganho K = 400 × 0,01 = 4", fontsize=11.5, color=GRAY)

    # 3
    x = 9.3
    ax.text(x, 4.6, r"estados: $x_1=y$,  $x_2=\dot{y}$", fontsize=13, color=GRAY)
    ax.text(x, 3.95, r"$\dot{x}_1=x_2$", fontsize=16, color=TXT)
    ax.text(x, 3.35, r"$\dot{x}_2=-133{,}3\,x_1-26{,}7\,x_2$", fontsize=14.5, color=TXT)
    ax.text(x, 2.9, r"$\qquad +\,533{,}3\,u$", fontsize=14.5, color=TXT)
    ax.text(x, 2.35, r"$y=x_1$", fontsize=16, color=TXT)
    ax.text(x, 1.75, "forma usada para integrar no\ncomputador (Runge-Kutta 4)", fontsize=11,
            color=GRAY, va="center", linespacing=1.3)
    return fig


def s_analise(d, num, total):
    m = d["m_ma"]
    fig, ax = novo_slide("Análise da planta (sozinha, em malha aberta)", num, total, etapa=1,
                         resumo=f"planta estável e sem oscilação, mas lenta (≈ {br(m['ts_2'])} s) e sem integrador (tipo 0)")
    t, u, y = d["ma"]
    ax.text(0.6, 5.45, "Aplicando u = 0,75 V direto no LED (sem realimentação):", fontsize=13, color=GRAY)
    ay, au = grafico_resposta(fig, 1.25, 1.85, 6.9, 3.35,
                              [(t, y, dict(color=ACC, lw=2.6, label="saída y(t)"))],
                              [(t, u, dict(color=RED, lw=2.0))], ylim_y=(0, 3.4), ylim_u=(-0.3, 5.7))
    ay.axhline(3.0, color=GRAY, ls="--", lw=1.2)
    ay.text(0.98, 3.08, "valor final = 4 × 0,75 = 3 V", ha="right", fontsize=10.5, color=GRAY)
    ay.axvline(m["ts_2"], color=ORANGE, ls=":", lw=1.6)
    ay.text(m["ts_2"] + 0.015, 1.0, f"acomoda em\n{br(m['ts_2'])} s", fontsize=10.5, color=ORANGE,
            weight="bold")

    props = [
        ("Polos", "s = −20 e s = −6,67 rad/s", "reais e negativos → estável, não oscila"),
        ("Ganho DC", "K = 4", "0,75 V na entrada → 3 V (300 lux)"),
        ("Rapidez", f"Ts ≈ {br(m['ts_2'])} s", "dominada pelo sensor (τ₂ = 0,15 s)"),
        ("Tipo 0", "sem integrador", "em malha fechada simples terá erro em regime"),
    ]
    yy = 5.05
    for tit, big, small in props:
        cor = RED if tit == "Tipo 0" else NAVY
        caixa(ax, 8.55, yy - 0.82, 4.18, 0.9, fc=RED_LIGHT if tit == "Tipo 0" else LIGHT)
        ax.text(8.75, yy - 0.2, tit, fontsize=12, color=GRAY, va="center")
        ax.text(10.0, yy - 0.2, big, fontsize=13.5, weight="bold", color=cor, va="center")
        ax.text(8.75, yy - 0.58, small, fontsize=11, color=TXT, va="center")
        yy -= 1.0
    return fig


def s_sem_controlador(d, num, total):
    fig, ax = novo_slide("Malha fechada sem controlador: o que dá errado", num, total, etapa=2,
                         resumo="sem controlador o sistema erra 20 % e oscila  →  é preciso projetar um controlador")
    t, r, y, u = d["sc"]
    m = d["m_sc"]

    # mini diagrama
    yc = 5.4
    ax.text(0.65, yc, "r", fontsize=15, weight="bold", color=TXT, va="center")
    seta(ax, 0.85, yc, 1.25, yc, ms=14, lw=2)
    ax.add_patch(Circle((1.42, yc), 0.17, fc="white", ec=NAVY, lw=1.8))
    ax.text(1.42, yc, "Σ", ha="center", va="center", fontsize=11, color=NAVY)
    seta(ax, 1.59, yc, 2.15, yc, ms=14, lw=2)
    ax.text(1.87, yc + 0.13, "u = r − y", fontsize=10, color=RED, ha="center")
    bloco(ax, 2.2, yc - 0.27, 1.1, 0.54, "G(s)", tsize=12)
    seta(ax, 3.3, yc, 3.85, yc, ms=14, lw=2)
    ax.text(4.0, yc, "y", fontsize=15, weight="bold", color=ACC, va="center")
    ax.plot([3.6, 3.6, 1.42], [yc, yc - 0.42, yc - 0.42], color=NAVY, lw=1.8)
    seta(ax, 1.42, yc - 0.42, 1.42, yc - 0.17, ms=12, lw=1.8)
    ax.text(4.45, yc, "realimentação unitária, degrau r = 3 V (300 lux)", fontsize=12.5,
            color=GRAY, va="center")

    ay, au = grafico_resposta(
        fig, 1.25, 1.85, 6.9, 2.95,
        [(t, r, dict(color="black", ls="--", lw=1.6, label="referência r(t)")),
         (t, y, dict(color=ACC, lw=2.6, label="saída y(t)"))],
        [(t, u, dict(color=RED, lw=2.0))])
    ay.legend(loc="lower right", frameon=False, fontsize=10.5)
    ay.annotate("", xy=(0.72, 3.0), xytext=(0.72, 2.4),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    ay.text(0.74, 2.7, "erro", color=RED, fontsize=11.5, weight="bold", va="center")
    i_pk = int(np.argmax(y))
    ay.annotate("oscila", xy=(t[i_pk], y[i_pk]), xytext=(0.3, 3.2), color=RED, fontsize=11.5,
                weight="bold", arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.5))

    problemas = [
        (f"{m['ess_pct']:.0f} %", "erro em regime", "para em 2,4 V (240 lux)\nem vez de 3 V (300 lux)"),
        (f"{m['po_regime_pct']:.0f} %", "de overshoot", "a luz passa do ponto\ne oscila antes de parar"),
        (f"{br(m['ts_2'])} s", "para acomodar", "dá para ser\nmais rápido"),
    ]
    yy = 4.85
    for big, mid, small in problemas:
        caixa(ax, 8.55, yy - 1.0, 4.18, 1.05, fc=RED_LIGHT)
        ax.add_patch(Rectangle((8.55, yy - 1.0), 0.09, 1.05, color=RED))
        ax.text(8.85, yy - 0.47, big, fontsize=23, weight="bold", color=RED, va="center")
        ax.text(10.35, yy - 0.3, mid, fontsize=13, weight="bold", color=TXT, va="center")
        ax.text(10.35, yy - 0.68, small, fontsize=10.3, color=GRAY, va="center", linespacing=1.2)
        yy -= 1.17
    return fig


def s_especificacoes(num, total):
    fig, ax = novo_slide("O que eu quero que o sistema faça", num, total, etapa=3,
                         resumo="4 especificações de desempenho para a malha fechada com controlador")

    ax.text(0.6, 5.4, "Especificações de desempenho desejadas", fontsize=15, weight="bold", color=GREEN)
    cab_y = 4.85
    ax.text(0.95, cab_y, "Especificação", fontsize=12, weight="bold", color=GRAY)
    ax.text(5.6, cab_y, "Sem controlador", fontsize=12, weight="bold", color=GRAY, ha="center")
    ax.text(7.75, cab_y, "Meta", fontsize=12, weight="bold", color=GRAY, ha="center")
    ax.text(8.9, cab_y, "Por quê?", fontsize=12, weight="bold", color=GRAY)
    linhas = [
        ("Erro em regime permanente", "20 %", "0 %", "a luz deve ficar exatamente no valor pedido"),
        ("Overshoot (P.O.)", "15 %", "≤ 5 %", "evitar \"flash\" de luz visível para o olho"),
        ("Tempo de acomodação (2 %)", "0,31 s", "≤ 0,30 s", "ajustar a luz mais rápido que hoje"),
        ("Sinal de controle u(t)", "0 a 3 V", "0 a 5 V", "limite físico do driver do LED"),
    ]
    yy = 4.15
    for esp, sem, meta, pq in linhas:
        caixa(ax, 0.6, yy - 0.38, 12.13, 0.76, fc=GREEN_LIGHT)
        ax.text(0.95, yy, esp, fontsize=14, color=TXT, va="center", weight="bold")
        ax.text(5.6, yy, sem, fontsize=14, color=RED, va="center", ha="center")
        ax.text(7.75, yy, meta, fontsize=17, color=GREEN, va="center", ha="center", weight="bold")
        ax.text(8.9, yy, pq, fontsize=12, color=TXT, va="center")
        yy -= 0.9
    return fig


def s_metodo(num, total):
    fig, ax = novo_slide("Tipo de controlador e método de projeto", num, total, etapa=3,
                         resumo="controlador digital de 2ª ordem com integrador, projetado pelo Método Polinomial (2ª Maneira)")

    # Duas maneiras do enunciado
    ax.text(0.6, 5.4, "O enunciado permite duas maneiras de projetar:", fontsize=13, color=GRAY)
    lanes = [
        (4.45, "1ª Maneira", ["Planta contínua", "Projeta C(s)\ncontínuo", "Discretiza\nC(s) → C(z)"], False),
        (3.05, "2ª Maneira", ["Planta contínua", "Discretiza a planta\nG(s) → G(z)", "Projeta C(z)\ndireto em z"], True),
    ]
    for y, nome, passos, escolhida in lanes:
        fc = ACC_LIGHT if escolhida else LIGHT
        ec = ACC if escolhida else "none"
        caixa(ax, 0.6, y - 0.55, 7.55, 1.15, fc=fc, ec=ec, lw=2)
        ax.text(0.85, y + 0.02, nome, fontsize=14, weight="bold", color=NAVY if escolhida else GRAY,
                va="center")
        x = 2.45
        for i, p in enumerate(passos):
            caixa(ax, x, y - 0.38, 1.6, 0.8, fc="white", ec=NAVY if escolhida else "#C5CDD6", lw=1.5, r=0.1)
            ax.text(x + 0.8, y + 0.02, p, ha="center", va="center", fontsize=10.2,
                    color=TXT if escolhida else GRAY, linespacing=1.15)
            if i < 2:
                seta(ax, x + 1.6, y + 0.02, x + 1.83, y + 0.02, ms=13, lw=1.8,
                     cor=NAVY if escolhida else "#C5CDD6")
            x += 1.85
        if escolhida:
            caixa(ax, 6.2, y + 0.42, 1.85, 0.36, fc=GREEN, r=0.16)
            ax.text(7.12, y + 0.6, "✔ usada", ha="center", va="center", fontsize=11, color="white",
                    weight="bold")

    ax.text(0.6, 1.85, "Por que a 2ª Maneira? O controlador é projetado já no tempo discreto,\n"
                       "ou seja, exatamente o algoritmo que o computador vai executar.",
            fontsize=12, color=TXT, va="center", linespacing=1.4)

    # Cartão do método
    caixa(ax, 8.5, 1.45, 4.23, 4.2, fc=LIGHT)
    ax.text(8.75, 5.2, "Método Polinomial", fontsize=16, weight="bold", color=NAVY)
    ax.text(8.75, 4.7, "Eu escolho onde ficam os polos\nda malha fechada e resolvo uma\nequação para achar C(z):",
            fontsize=11.5, color=TXT, va="top", linespacing=1.35)
    ax.text(10.6, 3.4, r"$a(z)\,\ell(z)+b(z)\,p(z)=a^*(z)$", fontsize=14.5, ha="center", color=NAVY)
    ax.text(8.75, 2.85, "a*(z) = polos desejados", fontsize=11, color=GRAY)
    ax.text(8.75, 2.35, "Incluo (z − 1) em ℓ(z):", fontsize=11.5, color=TXT, weight="bold")
    ax.text(8.75, 1.95, "é um integrador → erro zero\npara referência em degrau", fontsize=11,
            color=GREEN, va="center", linespacing=1.3)
    return fig


def s_projeto(d, num, total):
    fig, ax = novo_slide("Projeto do controlador passo a passo", num, total, etapa=3,
                         resumo="resolvendo a equação com os polos escolhidos, obtenho o controlador C(z) abaixo")
    b, a = d["b"], d["a"]

    y0, h0 = 2.85, 2.75
    passos = [(0.6, "1", "Amostragem (regra do trabalho)"), (4.75, "2", "Discretizar a planta (ZOH)"),
              (8.9, "3", "Escolher polos e resolver")]
    for x, n, tit in passos:
        caixa(ax, x, y0, 3.83, h0, fc=LIGHT)
        ax.add_patch(Circle((x + 0.45, y0 + h0 - 0.42), 0.24, color=ACC))
        ax.text(x + 0.45, y0 + h0 - 0.42, n, ha="center", va="center", fontsize=13, weight="bold",
                color="white")
        ax.text(x + 0.82, y0 + h0 - 0.42, tit, va="center", fontsize=13, weight="bold", color=NAVY)
    for xa in [4.46, 8.61]:
        seta(ax, xa, y0 + h0 / 2, xa + 0.25, y0 + h0 / 2, ms=16)

    x = 0.85
    ax.text(x, 4.55, r"$\tau_{min}=0{,}05$ s", fontsize=14, color=TXT)
    ax.text(x, 4.0, r"passo da planta: $\tau_{min}/100=0{,}5$ ms", fontsize=12, color=TXT)
    ax.text(x, 3.5, r"amostragem: $h=\tau_{min}/10=5$ ms", fontsize=12, color=NAVY, weight="bold")
    ax.text(x, 3.08, "→ 10 passos da planta por amostra", fontsize=11, color=GRAY)

    xc = 4.75 + 1.915
    ax.text(xc, 4.05, rf"$G(z)=\dfrac{{{br(b[0], 5)}\,z+{br(b[1], 5)}}}{{z^2-{br(-a[1], 3)}\,z+{br(a[2], 3)}}}$",
            fontsize=14, ha="center", va="center", color=NAVY)
    ax.text(5.0, 3.15, "conversão exata da planta para o\ntempo discreto (segurador ZOH)", fontsize=11,
            color=GRAY, va="center", linespacing=1.3)

    x = 9.15
    ax.text(x, 4.6, "polos desejados (em s):", fontsize=11.5, color=GRAY)
    ax.text(x, 4.15, "−10, −10, −25, −25 rad/s", fontsize=13.5, color=NAVY, weight="bold")
    ax.text(x, 3.7, r"em z ($z=e^{sh}$): 0,951 (×2) e 0,882 (×2)", fontsize=11, color=TXT)
    ax.text(x, 3.15, "sistema linear 4×4 → solução única", fontsize=11, color=GRAY)

    caixa(ax, 0.6, 1.35, 12.13, 1.3, fc=ACC_LIGHT, ec=ACC, lw=2)
    ax.text(0.95, 2.0, "Controlador\nobtido", fontsize=14, weight="bold", color=NAVY, va="center",
            linespacing=1.2)
    ax.text(7.1, 2.0,
            r"$C(z)=\dfrac{U(z)}{E(z)}=\dfrac{0{,}7857\,z^2-1{,}4699\,z+0{,}6868}{(z-1)(z-0{,}8004)}$",
            fontsize=20, ha="center", va="center", color=NAVY)
    ax.text(11.4, 1.6, "← integrador", fontsize=10.5, color=GREEN, weight="bold")
    return fig


def s_algoritmo(d, num, total):
    fig, ax = novo_slide("Algoritmo do controlador", num, total, etapa=3,
                         resumo="a cada 5 ms: lê o sensor, calcula o erro, calcula u e envia ao LED (fica constante até a próxima amostra)")
    caixa(ax, 0.6, 1.4, 6.9, 4.25, fc="#1C222B", r=0.12)
    codigo = (
        "// h = 0,005 s\n"
        "uant1 = uant2 = eant1 = eant2 = 0;\n"
        "while (loop) {               // a cada h\n"
        "   y = vin1();               // lê sensor (A/D)\n"
        "   e = r - y;                // erro\n"
        "   u = 1.800410*uant1 - 0.800410*uant2\n"
        "     + 0.785669*e - 1.469869*eant1\n"
        "     + 0.686831*eant2;\n"
        "   uant2 = uant1;  uant1 = u;\n"
        "   eant2 = eant1;  eant1 = e;\n"
        "   vout1(u);                 // envia (D/A)\n"
        "}"
    )
    ax.text(0.85, 5.4, codigo, family="DejaVu Sans Mono", fontsize=12, color="#E6EDF3", va="top",
            linespacing=1.5)

    # Princípio do ZOH
    caixa(ax, 7.8, 1.4, 4.93, 4.25, fc=LIGHT)
    ax.text(8.05, 5.25, "Princípio do ZOH (pedido no trabalho)", fontsize=13, weight="bold", color=NAVY)
    tc, rc, yc, uc = d["cc"]
    ap = eixo(fig, 8.45, 2.35, 4.0, 2.4)
    m = tc <= 0.0401
    ap.plot(tc[m], uc[m], drawstyle="steps-post", color=RED, lw=2)
    ap.plot(tc[m][::1], uc[m][::1], ".", color=NAVY, ms=2.5)
    ap.set_xticks([0, 0.01, 0.02, 0.03, 0.04])
    ap.set_xticklabels(["0", "10", "20", "30", "40"])
    ap.set_xlabel("tempo [ms]", fontsize=10.5)
    ap.set_ylabel("u(t) [V]", fontsize=10.5)
    ap.tick_params(labelsize=9.5)
    ap.grid(True, color="#E3E8EE", lw=0.8)
    ax.text(8.05, 1.75, "cada degrau dura h = 5 ms = 10 passos (pontos)\nda simulação da planta",
            fontsize=10.5, color=GRAY, va="center", linespacing=1.3)
    return fig


def s_com_controlador(d, num, total):
    fig, ax = novo_slide("Malha fechada com o controlador: metas atingidas", num, total, etapa=4,
                         resumo="erro zerado, quase sem overshoot, mais rápido e com u dentro do limite do driver")
    ts, rs, ysc, usc = d["sc"]
    tc, rc, ycc, ucc = d["cc"]
    msc, mcc = d["m_sc"], d["m_cc"]

    ax.text(0.6, 5.45, "Mesmo degrau de 3 V (300 lux), agora com C(z):", fontsize=13, color=GRAY)
    ay, au = grafico_resposta(
        fig, 1.25, 1.85, 6.9, 3.35,
        [(ts, rs, dict(color="black", ls="--", lw=1.6, label="referência")),
         (ts, ysc, dict(color="#AAB4BF", lw=2.0, label="sem controlador")),
         (tc, ycc, dict(color=ACC, lw=2.8, label="com controlador"))],
        [(ts, usc, dict(color="#AAB4BF", lw=1.6)), (tc, ucc, dict(color=RED, lw=2.0))])
    ay.legend(loc="lower right", frameon=False, fontsize=10.5)

    x0, y0, w0, h0 = 8.55, 1.45, 4.18, 4.2
    caixa(ax, x0, y0, w0, h0, fc=LIGHT)
    cx = [x0 + 0.2, x0 + 1.95, x0 + 2.95, x0 + 4.0]
    yy = y0 + h0 - 0.35
    for c, txt, ha in zip(cx, ["", "Sem", "Com", "Meta"], ["left", "center", "center", "right"]):
        ax.text(c, yy, txt, fontsize=12.5, weight="bold", color=GRAY, ha=ha, va="center")
    linhas = [
        ("Erro em\nregime", f"{msc['ess_pct']:.0f} %", f"{abs(mcc['ess_pct']):.0f} %", "0 %"),
        ("Overshoot", f"{msc['po_regime_pct']:.0f} %", f"{br(mcc['po_ref_pct'], 1)} %", "≤ 5 %"),
        ("Acomodação", f"{br(msc['ts_2'])} s", f"{br(mcc['ts_2'])} s", "≤ 0,30 s"),
        ("u máximo", f"{br(np.max(usc), 1)} V", f"{br(np.max(ucc), 1)} V", "≤ 5 V"),
    ]
    yy -= 0.68
    for i, (lab, s, c, meta) in enumerate(linhas):
        ax.text(cx[0], yy, lab, fontsize=12, color=TXT, va="center", linespacing=1.1)
        ax.text(cx[1], yy, s, fontsize=12.5, color=RED if lab != "u máximo" else GRAY, ha="center", va="center")
        ax.text(cx[2], yy, c, fontsize=13.5, color=GREEN, weight="bold", ha="center", va="center")
        ax.text(cx[3], yy, meta, fontsize=11, color=GRAY, ha="right", va="center")
        if i < len(linhas) - 1:
            ax.plot([x0 + 0.2, x0 + w0 - 0.2], [yy - 0.36, yy - 0.36], color="#DDE3EA", lw=1)
        yy -= 0.72
    caixa(ax, x0 + 0.2, y0 + 0.18, w0 - 0.4, 0.55, fc=GREEN, r=0.26)
    ax.text(x0 + w0 / 2, y0 + 0.455, "✔ 4 de 4 metas atendidas", fontsize=13.5, weight="bold",
            color="white", ha="center", va="center")
    return fig


def s_ajuste(d, num, total):
    fig, ax = novo_slide("Ajuste fino: por que esses polos?", num, total, etapa=4,
                         resumo="polos mais rápidos pioraram o overshoot e estouraram o driver  →  suavizei os polos")
    t1, r1, y1, u1 = d["t1"]
    tc, rc, yc, uc = d["cc"]
    m1, mc = d["m_t1"], d["m_cc"]

    ay, au = grafico_resposta(
        fig, 1.25, 1.85, 6.9, 3.70,
        [(t1, r1, dict(color="black", ls="--", lw=1.6, label="referência")),
         (t1, y1, dict(color=ORANGE, lw=2.2, label="1ª tentativa (−18, −30)")),
         (tc, yc, dict(color=ACC, lw=2.6, label="final (−10, −25)"))],
        [(t1, u1, dict(color=ORANGE, lw=1.8)), (tc, uc, dict(color=RED, lw=2.0))],
        ylim_y=(0, 3.5), ylim_u=(-0.3, 7.9))
    ay.legend(loc="lower right", frameon=False, fontsize=10.5)

    caixa(ax, 8.55, 3.65, 4.18, 2.0, fc=ORANGE_LIGHT)
    ax.text(8.8, 5.25, "1ª tentativa: polos −18 e −30", fontsize=13.5, weight="bold", color="#9C640C")
    ax.text(8.8, 4.8, f"✘ overshoot de {br(m1['po_ref_pct'], 1)} % (> 5 %)\n"
                      f"✘ u chega a {br(np.max(u1), 1)} V (> 5 V)",
            fontsize=12.5, color=TXT, va="top", linespacing=1.55)

    caixa(ax, 8.55, 1.45, 4.18, 2.0, fc=GREEN_LIGHT)
    ax.text(8.8, 3.05, "Final: polos −10 e −25", fontsize=13.5, weight="bold", color=GREEN)
    ax.text(8.8, 2.6, f"✔ overshoot de {br(mc['po_ref_pct'], 1)} %\n"
                      f"✔ u máximo de {br(np.max(uc), 1)} V\n"
                      f"✔ acomoda em {br(mc['ts_2'])} s",
            fontsize=12.5, color=TXT, va="top", linespacing=1.45)
    return fig


def s_conclusao(num, total):
    fig, ax = novo_slide("Conclusão", num, total, etapa=None,
                         resumo="o controlador digital fez a luz chegar exatamente em 300 lux, rápido e sem piscar")
    itens = [
        ("A planta", "LED + sensor LDR, modelada como dois\nblocos de 1ª ordem → G(s) de 2ª ordem."),
        ("Sem controlador", "erro de 20 % e overshoot de 15 %."),
        ("Projeto", "controlador digital de 2ª ordem com\nintegrador, pelo Método Polinomial."),
        ("Com controlador", "erro 0 %, overshoot 0,9 %, acomoda\nem 0,26 s e u ≤ 2,4 V: metas atendidas."),
    ]
    yy = 5.25
    for i, (tit, txt) in enumerate(itens, 1):
        ax.add_patch(Circle((0.95, yy - 0.12), 0.25, color=ACC))
        ax.text(0.95, yy - 0.12, str(i), ha="center", va="center", fontsize=13, weight="bold", color="white")
        ax.text(1.4, yy, tit, fontsize=15, weight="bold", color=NAVY, va="center")
        ax.text(1.4, yy - 0.32, txt, fontsize=12.5, color=TXT, va="top", linespacing=1.3)
        yy -= 1.0

    caixa(ax, 8.1, 1.4, 4.63, 4.25, fc=NAVY, r=0.18)
    ax.text(10.42, 5.25, "Teste você mesmo", ha="center", fontsize=15, weight="bold", color="white")
    caixa(ax, 9.27, 2.4, 2.3, 2.4, fc="white", r=0.1)
    ax_qr = eixo(fig, 9.37, 2.5, 2.1, 2.2)
    ax_qr.imshow(qr_image(URL_SIMULADOR), interpolation="nearest")
    ax_qr.axis("off")
    ax.text(10.42, 2.0, URL_SIMULADOR.replace("https://", ""), ha="center", fontsize=9.3, color="#D2E2F4")
    ax.text(10.42, 1.65, "Obrigado!  Perguntas?", ha="center", fontsize=13, weight="bold", color=YELLOW)
    return fig


# ------------------------------------------------------------------------------
# Roteiro de fala (≈ 9 min 30 s)
# ------------------------------------------------------------------------------
ROTEIRO = [
    ("Capa", "15 s",
     "Meu trabalho é o controle digital de iluminação: manter a luz de uma bancada num valor desejado "
     "usando um LED, um sensor de luz e um controlador digital. O QR code abre o simulador online do projeto."),
    ("A planta", "50 s",
     "A planta é uma luminária de LED sobre uma bancada. O objetivo é manter a iluminação num valor, "
     "por exemplo 300 lux, que é o recomendado para escritórios. Um sensor de luz, o LDR, fica na bancada; "
     "o computador lê esse sensor e ajusta a tensão do LED. A entrada da planta é a tensão no driver do LED, "
     "de 0 a 5 V, e a saída é a tensão do sensor, calibrada para 1 V igual a 100 lux."),
    ("Componentes", "50 s",
     "A planta tem dois blocos. O driver do LED transforma tensão em luz; ele tem um filtro RC que suaviza o PWM, "
     "então demora um pouco para responder: constante de tempo de 0,05 s, com ganho de 400 lux por volt. "
     "O sensor LDR transforma luz em tensão; somando a inércia do LDR com o filtro anti-ruído, a constante de tempo "
     "é 0,15 s, com 0,01 V por lux. A constante de tempo é o tempo de reação: em t = τ o bloco chega a 63 % do valor final. "
     "Dois blocos de primeira ordem em série dão uma planta de segunda ordem."),
    ("Modelagem", "1 min",
     "Cada bloco é uma equação diferencial de primeira ordem. Aplicando Laplace e multiplicando os dois blocos, "
     "chego na função de transferência G(s) = 4 sobre (0,05s + 1)(0,15s + 1). O ganho 4 é 400 vezes 0,01. "
     "Em variáveis de estado, uso x1 = y e x2 = derivada de y, que é a forma que eu integro no computador com Runge-Kutta."),
    ("Análise da planta", "40 s",
     "Analisando a planta sozinha: aplicando 0,75 V no LED, a saída vai para 3 V, porque o ganho é 4. "
     "Os polos são -20 e -6,67: reais e negativos, então é estável e não oscila. Mas é lenta, cerca de 0,63 s, "
     "e é tipo 0, sem integrador, o que já indica erro em regime quando fechar a malha."),
    ("Sem controlador", "1 min",
     "Fechando a malha sem controlador, ou seja, u = r - y, com degrau de 3 V: aparecem três problemas. "
     "Erro em regime de 20 %: a luz para em 240 lux em vez de 300. Overshoot de 15 %: a luz passa do ponto e oscila. "
     "E leva 0,31 s para acomodar. Isso acontece porque a planta não tem integrador e a malha fechada fica subamortecida."),
    ("Especificações", "40 s",
     "A partir disso defini quatro especificações: erro em regime zero, para a luz ficar exatamente no valor pedido; "
     "overshoot de no máximo 5 %, para não dar flash de luz; tempo de acomodação até 0,30 s, mais rápido que hoje; "
     "e sinal de controle entre 0 e 5 V, que é o limite físico do driver."),
    ("Método", "1 min",
     "O enunciado permite duas maneiras. Na primeira projeta-se contínuo e depois discretiza o controlador. "
     "Eu usei a segunda: discretizo a planta e projeto o controlador direto no tempo discreto, que é exatamente o "
     "algoritmo que o computador executa. O método foi o Polinomial: eu escolho os polos da malha fechada e resolvo "
     "a equação a(z)ℓ(z) + b(z)p(z) = a*(z). Colocando o fator (z - 1) em ℓ(z) eu incluo um integrador, que garante erro zero."),
    ("Projeto", "1 min",
     "Passo 1: a menor constante de tempo é 0,05 s, então pela regra do trabalho a planta é simulada com passo de 0,5 ms "
     "e o controlador amostra a cada 5 ms, ou seja, 10 passos da planta por amostra. "
     "Passo 2: discretizo a planta com o segurador de ordem zero e obtenho G(z). "
     "Passo 3: escolho os polos em -10, -10, -25 e -25 rad/s, resolvo o sistema e chego neste controlador C(z), "
     "que tem o integrador (z - 1) no denominador."),
    ("Algoritmo", "30 s",
     "Este é o algoritmo: a cada 5 ms ele lê o sensor, calcula o erro, calcula u com a equação a diferenças e envia ao LED. "
     "Como pede o trabalho, u fica constante durante a amostra: cada degrau dura 10 passos da simulação da planta."),
    ("Com controlador", "1 min",
     "Com o controlador, a curva azul é a nova resposta e a cinza é a antiga. O erro em regime foi de 20 % para zero, "
     "o overshoot de 15 % para 0,9 %, o tempo de acomodação de 0,31 para 0,26 s, e o sinal de controle ficou no máximo "
     "em 2,4 V, dentro do limite de 5 V. As quatro especificações foram atendidas."),
    ("Ajuste fino", "30 s",
     "Esses polos vieram de um ajuste fino. Na primeira tentativa usei polos mais rápidos, -18 e -30: o overshoot foi 8,8 % "
     "e o sinal de controle passou de 7 V, acima do limite do driver. Suavizando para -10 e -25, tudo foi atendido."),
    ("Conclusão", "20 s",
     "Resumindo: modelei a planta LED mais LDR como segunda ordem, sem controlador ela errava 20 % e oscilava, "
     "e com o controlador polinomial com integrador todas as metas foram atendidas. O simulador está online no QR code. Obrigado."),
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
    for f in os.listdir(SLIDES_DIR):
        os.remove(os.path.join(SLIDES_DIR, f))
    d = calcular_dados()
    construtores = [
        lambda n, T: s_capa(T),
        lambda n, T: s_planta(n, T),
        lambda n, T: s_componentes(d, n, T),
        lambda n, T: s_modelagem(n, T),
        lambda n, T: s_analise(d, n, T),
        lambda n, T: s_sem_controlador(d, n, T),
        lambda n, T: s_especificacoes(n, T),
        lambda n, T: s_metodo(n, T),
        lambda n, T: s_projeto(d, n, T),
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
