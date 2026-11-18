"""
Simulação do Sistema de Controle Digital de Iluminação Adaptativa
-----------------------------------------------------------------
Planta: Driver LED (tau1 = 0,05 s) + Sensor LDR condicionado (tau2 = 0,15 s), K = 4,0 V/V.
Projeto do Controlador: Segunda Maneira (Discretização ZOH da planta + Método Polinomial).
Regras da disciplina:
  - Passo de integração da planta: dt = tau_min / 100 = 0,0005 s
  - Intervalo de amostragem do controlador: h = tau_min / 10 = 0,005 s (ZOH de 10 iterações)
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt


# ==============================================================================
# 1. PARÂMETROS FÍSICOS DA PLANTA E TEMPOS DE SIMULAÇÃO
# ==============================================================================
TAU_1 = 0.05      # Constante de tempo do driver de corrente do LED [s]
TAU_2 = 0.15      # Constante de tempo do sensor LDR + filtro condicionador [s]
K_LED = 400.0     # Ganho do driver + luminária LED [lux/V]
K_LDR = 0.01      # Ganho do circuito condicionador do sensor LDR [V/lux]
K_PLANTA = K_LED * K_LDR  # Ganho DC total da planta = 4,0 [V/V]

TAU_MIN = min(TAU_1, TAU_2)  # 0,05 s
DT = TAU_MIN / 100.0         # Passo de integração = 0,0005 s
H = TAU_MIN / 10.0           # Período de amostragem = 0,005 s
PASSOS_POR_AMOSTRA = 10      # h / dt = 10 iterações da planta por amostra

# Coeficientes da EDO contínua: y'' + a1_c*y' + a0_c*y = b0_c*u
A0_C = 1.0 / (TAU_1 * TAU_2)
A1_C = (1.0 / TAU_1) + (1.0 / TAU_2)
B0_C = K_PLANTA / (TAU_1 * TAU_2)

# Limites físicos do driver LED (0 V a 5 V)
U_MIN_FISICO = 0.0
U_MAX_FISICO = 5.0


# ==============================================================================
# 2. DISCRETIZAÇÃO EXATA VIA ZOH E PROJETO PELO MÉTODO POLINOMIAL
# ==============================================================================
def discretizar_planta_zoh(tau1: float, tau2: float, k_dc: float, h: float):
    """Calcula G(z) = b(z)/a(z) exata via Amostrador-Retentor de Ordem Zero (ZOH)."""
    p1 = 1.0 / tau1
    p2 = 1.0 / tau2
    e1 = np.exp(-p1 * h)
    e2 = np.exp(-p2 * h)

    # Frações parciais de G(s)/s = A/s + B/(s+p1) + C/(s+p2)
    coef_a = k_dc
    coef_b = k_dc * p1 * p2 / (-p1 * (-p1 + p2))
    coef_c = k_dc * p1 * p2 / (-p2 * (-p2 + p1))

    # Numerador b(z) = b1*z + b0 e denominador a(z) = z^2 + a1*z + a0
    b1 = -coef_a * (e1 + e2) - coef_b * (1.0 + e2) - coef_c * (1.0 + e1)
    b0 = coef_a * e1 * e2 + coef_b * e2 + coef_c * e1

    b_poly = np.array([b1, b0], dtype=float)
    a_poly = np.poly([e1, e2]).astype(float)
    return b_poly, a_poly, e1, e2


def projetar_controlador_polinomial(b_poly: np.ndarray, a_poly: np.ndarray,
                                    polos_s: list, h: float):
    """
    Resolve a Equação Diofantina com Princípio do Modelo Interno para degrau:
        a(z)*(z - 1)*l2(z) + b(z)*p(z) = a*(z)
    onde l2(z) = z + l20 e p(z) = p2*z^2 + p1*z + p0.
    Retorna ell(z) = [1, ell_1, ell_0] e p(z) = [p2, p1, p0].
    """
    polos_z = [np.exp(s * h) for s in polos_s]
    a_star = np.real(np.poly(polos_z))

    # a_tilde(z) = a(z) * (z - 1) -> grau 3
    a_tilde = np.polymul(a_poly, [1.0, -1.0])

    # Equação linear para [l20, p2, p1, p0] igualando termos em z^3, z^2, z^1, z^0
    rhs = a_star[1:] - np.array([a_tilde[1], a_tilde[2], a_tilde[3], 0.0])
    matriz_diofantina = np.array([
        [a_tilde[0], b_poly[0], 0.0,       0.0],
        [a_tilde[1], b_poly[1], b_poly[0], 0.0],
        [a_tilde[2], 0.0,       b_poly[1], b_poly[0]],
        [a_tilde[3], 0.0,       0.0,       b_poly[1]],
    ], dtype=float)

    l20, p2, p1, p0 = np.linalg.solve(matriz_diofantina, rhs)
    ell_poly = np.polymul([1.0, -1.0], [1.0, l20])
    p_poly = np.array([p2, p1, p0], dtype=float)

    return ell_poly, p_poly, polos_z, a_star


# ==============================================================================
# 3. INTEGRAÇÃO CONTÍNUA DA PLANTA (RK4) E SIMULAÇÃO EM MALHA FECHADA
# ==============================================================================
def passo_rk4_planta(x1: float, x2: float, u: float, dt: float):
    """Integra um passo dt da planta contínua usando Runge-Kutta de 4ª ordem."""
    def derivadas(s1, s2):
        return s2, -A0_C * s1 - A1_C * s2 + B0_C * u

    k1_1, k1_2 = derivadas(x1, x2)
    k2_1, k2_2 = derivadas(x1 + 0.5 * dt * k1_1, x2 + 0.5 * dt * k1_2)
    k3_1, k3_2 = derivadas(x1 + 0.5 * dt * k2_1, x2 + 0.5 * dt * k2_2)
    k4_1, k4_2 = derivadas(x1 + dt * k3_1, x2 + dt * k3_2)

    x1_prox = x1 + (dt / 6.0) * (k1_1 + 2.0 * k2_1 + 2.0 * k3_1 + k4_1)
    x2_prox = x2 + (dt / 6.0) * (k1_2 + 2.0 * k2_2 + 2.0 * k3_2 + k4_2)
    return x1_prox, x2_prox


def simular_sem_controlador(ref_func, t_total: float):
    """Simula a planta em malha fechada contínua sem controlador: u(t) = r(t) - y(t)."""
    n_passos = int(round(t_total / DT))
    t_hist = np.zeros(n_passos)
    r_hist = np.zeros(n_passos)
    y_hist = np.zeros(n_passos)
    u_hist = np.zeros(n_passos)

    x1, x2 = 0.0, 0.0
    for idx in range(n_passos):
        t = idx * DT
        r = ref_func(t)
        u = r - x1
        t_hist[idx] = t
        r_hist[idx] = r
        y_hist[idx] = x1
        u_hist[idx] = u
        x1, x2 = passo_rk4_planta(x1, x2, u, DT)

    return t_hist, r_hist, y_hist, u_hist


def simular_com_controlador(ref_func, t_total: float,
                            ell_poly: np.ndarray, p_poly: np.ndarray):
    """
    Simula a planta em malha fechada com o controlador discreto (ZOH):
    a cada período h = 10 * dt, lê y(k), calcula u(k) pelo algoritmo do controlador
    e mantém u(t) = u(k) constante durante 10 passos de integração da planta.
    """
    n_amostras = int(round(t_total / H))
    n_passos = n_amostras * PASSOS_POR_AMOSTRA

    t_hist = np.zeros(n_passos)
    r_hist = np.zeros(n_passos)
    y_hist = np.zeros(n_passos)
    u_hist = np.zeros(n_passos)

    # Parâmetros do algoritmo do controlador:
    # ell_0*u(k) + ell_1*u(k-1) + ell_2*u(k-2) = p2*e(k) + p1*e(k-1) + p0*e(k-2)
    ell1, ell0 = ell_poly[1], ell_poly[2]
    p2, p1, p0 = p_poly[0], p_poly[1], p_poly[2]

    # Inicialização das memórias do algoritmo
    u_ant1, u_ant2 = 0.0, 0.0
    e_ant1, e_ant2 = 0.0, 0.0
    x1, x2 = 0.0, 0.0

    idx = 0
    for k in range(n_amostras):
        t_amostra = k * H
        y_medido = x1
        r_atual = ref_func(t_amostra)
        e_atual = r_atual - y_medido

        # Lei de controle discreta (equação a diferenças)
        u_atual = (-ell1 * u_ant1 - ell0 * u_ant2
                   + p2 * e_atual + p1 * e_ant1 + p0 * e_ant2)

        # Atualização dos estados passados do controlador
        u_ant2, u_ant1 = u_ant1, u_atual
        e_ant2, e_ant1 = e_ant1, e_atual

        # ZOH: aplica u_atual constante por 10 passos de integração da planta
        for _ in range(PASSOS_POR_AMOSTRA):
            t_atual = idx * DT
            t_hist[idx] = t_atual
            r_hist[idx] = ref_func(t_atual)
            y_hist[idx] = x1
            u_hist[idx] = u_atual
            x1, x2 = passo_rk4_planta(x1, x2, u_atual, DT)
            idx += 1

    return t_hist, r_hist, y_hist, u_hist


def calcular_metricas_degrau(t_hist: np.ndarray, y_hist: np.ndarray, r_val: float):
    """Calcula erro em regime permanente, ultrapassagem percentual e Ts(2%)."""
    y_final = y_hist[-1]
    ess_abs = r_val - y_final
    ess_pct = (ess_abs / r_val) * 100.0

    y_pico = np.max(y_hist)
    po_ref_pct = max(0.0, (y_pico - r_val) / r_val * 100.0)
    po_regime_pct = max(0.0, (y_pico - y_final) / y_final * 100.0) if y_final > 0 else 0.0

    fora_faixa = np.where(np.abs(y_hist - y_final) > 0.02 * abs(y_final))[0]
    ts_2 = t_hist[fora_faixa[-1] + 1] if len(fora_faixa) > 0 and fora_faixa[-1] + 1 < len(t_hist) else t_hist[-1]
    return {
        "y_final": y_final,
        "ess_abs": ess_abs,
        "ess_pct": ess_pct,
        "y_pico": y_pico,
        "po_ref_pct": po_ref_pct,
        "po_regime_pct": po_regime_pct,
        "ts_2": ts_2,
    }


# ==============================================================================
# 4. GERAÇÃO DOS GRÁFICOS PADRÃO EXIGIDO (REFERÊNCIA+SAÍDA E ENTRADA)
# ==============================================================================
def salvar_figura_simulacao(caminho: str, titulo: str,
                            t_hist: np.ndarray, r_hist: np.ndarray,
                            y_hist: np.ndarray, u_hist: np.ndarray,
                            zoom_zoh: bool = False):
    """Gera figura com dois gráficos: (1) Referência e Saída y(t); (2) Entrada u(t)."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.5, 6.2), sharex=True)

    ax1.plot(t_hist, r_hist, "k--", linewidth=1.6, label="Referência $r(t)$ [V]")
    ax1.plot(t_hist, y_hist, color="#1f77b4", linewidth=2.0, label="Saída da planta $y(t)$ [V]")
    ax1.set_ylabel("Tensão do Sensor [V]\n(1 V = 100 lux)")
    ax1.set_title(titulo, fontsize=11.5, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.65)
    ax1.legend(loc="best", frameon=True)

    ax2.step(t_hist, u_hist, where="post", color="#d62728", linewidth=1.8,
             label="Entrada da planta $u(t)$ [V]")
    ax2.axhline(U_MAX_FISICO, color="gray", linestyle="-.", linewidth=1.0,
                label="Limite físico do driver (5,0 V)")
    ax2.axhline(U_MIN_FISICO, color="gray", linestyle=":", linewidth=1.0)
    ax2.set_xlabel("Tempo $t$ [s]")
    ax2.set_ylabel("Sinal de Controle $u(t)$ [V]")
    ax2.grid(True, linestyle=":", alpha=0.65)

    if zoom_zoh:
        ax2.set_ylim(-0.35, 5.6)
        ax2.legend(loc="upper left", bbox_to_anchor=(0.08, 0.88), frameon=True)
        # Inset mostrando os degraus ZOH de duração h = 5 ms (10 passos dt)
        ax_in = ax2.inset_axes([0.52, 0.31, 0.44, 0.48])
        mascara = t_hist <= 0.06
        ax_in.step(t_hist[mascara], u_hist[mascara], where="post",
                   color="#d62728", linewidth=1.4)
        ax_in.set_title("Detalhe dos pulsos ZOH ($h = 5\\,\\mathrm{ms}$)", fontsize=8.5)
        ax_in.set_xlabel("$t$ [s]", fontsize=8)
        ax_in.tick_params(labelsize=7.5)
        ax_in.grid(True, linestyle=":", alpha=0.6)
    else:
        ax2.legend(loc="best", frameon=True)

    plt.tight_layout()
    plt.savefig(caminho, dpi=180)
    return fig


def main():
    parser = argparse.ArgumentParser(description="Simulação - Controle de Iluminação")
    parser.add_argument("--show", action="store_true",
                        help="Exibe os gráficos na tela após salvar os arquivos PNG.")
    args = parser.parse_args()

    os.makedirs("figuras", exist_ok=True)
    r_degrau = 3.0  # Referência: 3,0 V = 300 lux

    # Discretização ZOH da planta
    b_poly, a_poly, e1, e2 = discretizar_planta_zoh(TAU_1, TAU_2, K_PLANTA, H)
    print("=== PARÂMETROS DA PLANTA ===")
    print(f"tau1 = {TAU_1} s, tau2 = {TAU_2} s, K = {K_PLANTA} V/V")
    print(f"tau_min = {TAU_MIN} s -> dt = {DT} s, h = {H} s (10 iteracoes/amostra)")
    print(f"Polos continuos: s1 = {-1/TAU_1:.2f} rad/s, s2 = {-1/TAU_2:.2f} rad/s")
    print(f"Polos discretos (h={H} s): z1 = {e1:.6f}, z2 = {e2:.6f}")
    print(f"G(z) num b(z) = {b_poly[0]:.8f}*z + {b_poly[1]:.8f}")
    print(f"G(z) den a(z) = z^2 + ({a_poly[1]:.8f})*z + {a_poly[2]:.8f}")
    print(f"Zero de G(z): z_0 = {-b_poly[1]/b_poly[0]:.6f}\n")

    # --------------------------------------------------------------------------
    # Simulação 1: Malha Fechada SEM Controlador
    # --------------------------------------------------------------------------
    t_nc, r_nc, y_nc, u_nc = simular_sem_controlador(lambda t: r_degrau, 1.00)
    met_nc = calcular_metricas_degrau(t_nc, y_nc, r_degrau)
    print("=== 1. MALHA FECHADA SEM CONTROLADOR (r = 3,0 V) ===")
    print(f"y_final = {met_nc['y_final']:.4f} V | e_ss = {met_nc['ess_abs']:.4f} V ({met_nc['ess_pct']:.2f}%)")
    print(f"y_pico  = {met_nc['y_pico']:.4f} V | P.O. (sobre y_ss) = {met_nc['po_regime_pct']:.2f}%")
    print(f"Ts(2%)  = {met_nc['ts_2']:.4f} s | u_max = {np.max(u_nc):.4f} V\n")

    salvar_figura_simulacao(
        "figuras/fig1_malha_fechada_sem_controlador.png",
        "Malha Fechada sem Controlador — Planta de Iluminação (Degrau $r = 3{,}0\\,\\mathrm{V}$)",
        t_nc, r_nc, y_nc, u_nc, zoom_zoh=False
    )

    # --------------------------------------------------------------------------
    # Simulação 2: Projeto Inicial (Tentativa 1: polos muito rápidos [-18,-18,-30,-30])
    # --------------------------------------------------------------------------
    polos_t1 = [-18.0, -18.0, -30.0, -30.0]
    ell_t1, p_t1, pz_t1, _ = projetar_controlador_polinomial(b_poly, a_poly, polos_t1, H)
    t_t1, r_t1, y_t1, u_t1 = simular_com_controlador(lambda t: r_degrau, 1.00, ell_t1, p_t1)
    met_t1 = calcular_metricas_degrau(t_t1, y_t1, r_degrau)
    print("=== 2. PROJETO INICIAL (TENTATIVA 1: s = {-18, -18, -30, -30}) ===")
    print(f"Polos em z: {np.round(pz_t1, 6)}")
    print(f"ell(z) = z^2 + ({ell_t1[1]:.6f})*z + ({ell_t1[2]:.6f})")
    print(f"p(z)   = {p_t1[0]:.6f}*z^2 + ({p_t1[1]:.6f})*z + ({p_t1[2]:.6f})")
    print(f"y_final = {met_t1['y_final']:.5f} V | P.O. = {met_t1['po_ref_pct']:.2f}% | Ts(2%) = {met_t1['ts_2']:.4f} s")
    print(f"u_min = {np.min(u_t1):.4f} V | u_max = {np.max(u_t1):.4f} V (excede 5 V!)\n")

    salvar_figura_simulacao(
        "figuras/fig2_malha_fechada_tentativa1.png",
        "Malha Fechada com Controlador Polinomial — 1ª Tentativa (Antes do Ajuste Fino)",
        t_t1, r_t1, y_t1, u_t1, zoom_zoh=False
    )

    # --------------------------------------------------------------------------
    # Simulação 3: Controlador Ajustado (Sintonia Final: s = [-10, -10, -25, -25])
    # --------------------------------------------------------------------------
    polos_fin = [-10.0, -10.0, -25.0, -25.0]
    ell_fin, p_fin, pz_fin, a_star_fin = projetar_controlador_polinomial(b_poly, a_poly, polos_fin, H)
    t_fin, r_fin, y_fin, u_fin = simular_com_controlador(lambda t: r_degrau, 1.00, ell_fin, p_fin)
    met_fin = calcular_metricas_degrau(t_fin, y_fin, r_degrau)
    print("=== 3. CONTROLADOR AJUSTADO (SINTONIA FINAL: s = {-10, -10, -25, -25}) ===")
    print(f"Polos em z: {np.round(pz_fin, 6)}")
    print(f"a*(z)  = {np.round(a_star_fin, 8)}")
    print(f"ell(z) = z^2 + ({ell_fin[1]:.6f})*z + ({ell_fin[2]:.6f})")
    print(f"p(z)   = {p_fin[0]:.6f}*z^2 + ({p_fin[1]:.6f})*z + ({p_fin[2]:.6f})")
    print(f"Zeros de p(z): {np.round(np.roots(p_fin), 6)}")
    print(f"y_final = {met_fin['y_final']:.5f} V | e_ss = {met_fin['ess_pct']:.4f}%")
    print(f"P.O. = {met_fin['po_ref_pct']:.2f}% | Ts(2%) = {met_fin['ts_2']:.4f} s")
    print(f"u_min = {np.min(u_fin):.4f} V | u_max = {np.max(u_fin):.4f} V | u_regime = {u_fin[-1]:.4f} V\n")

    salvar_figura_simulacao(
        "figuras/fig3_malha_fechada_ajustado.png",
        "Malha Fechada com Controlador Polinomial Ajustado — Resposta ao Degrau ($r = 3{,}0\\,\\mathrm{V}$)",
        t_fin, r_fin, y_fin, u_fin, zoom_zoh=True
    )

    # --------------------------------------------------------------------------
    # Simulação 4: Teste com Referência Constante por Partes (Múltiplos Degraus)
    # --------------------------------------------------------------------------
    def ref_multiplos_degraus(t: float) -> float:
        if t < 0.70:
            return 2.0   # 200 lux
        if t < 1.40:
            return 4.0   # 400 lux
        return 3.0       # 300 lux

    t_md, r_md, y_md, u_md = simular_com_controlador(ref_multiplos_degraus, 2.10, ell_fin, p_fin)
    print("=== 4. ENSAIO COMPLEMENTAR: MÚLTIPLOS DEGRAUS (2,0 V -> 4,0 V -> 3,0 V) ===")
    print(f"u_min = {np.min(u_md):.4f} V | u_max = {np.max(u_md):.4f} V")
    print(f"y(0,699s) = {y_md[int(0.699/DT)]:.5f} V | y(1,399s) = {y_md[int(1.399/DT)]:.5f} V | y(2,099s) = {y_md[-1]:.5f} V")

    salvar_figura_simulacao(
        "figuras/fig4_seguimento_multiplos_degraus.png",
        "Malha Fechada com Controlador Ajustado — Seguimento de Referência em Degraus",
        t_md, r_md, y_md, u_md, zoom_zoh=False
    )

    print("\nFiguras salvas com sucesso em ./figuras/")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
