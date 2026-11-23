# Roteiro da apresentação (≈ 9 min 30 s)

Simulador online: https://matteopeixotooo.github.io/Driver-LED-Project/

## Slide 1 — Capa (20 s)

Meu trabalho é o controle digital de iluminação adaptativa: manter uma bancada em 300 lux usando driver LED, sensor LDR e controlador projetado pelo Método Polinomial. O QR code abre o simulador online.

## Slide 2 — A planta (45 s)

A planta é uma luminária LED sobre uma bancada. A entrada u é a tensão no driver, de 0 a 5 V, e a saída y é a tensão do sensor LDR calibrada para 1 V igual a 100 lux. O objetivo é manter a luz exatamente no valor desejado.

## Slide 3 — Modelagem (1 min)

Modelando cada bloco por uma equação diferencial de 1ª ordem e aplicando Laplace, temos 400/(0,05s+1) para o LED e 0,01/(0,15s+1) para o LDR. Multiplicando, chegamos a G(s) = 4 / [(0,05s+1)(0,15s+1)], de 2ª ordem, Tipo 0, com polos em -20 e -6,67 rad/s. Também escrevo em variáveis de estado para integrar por RK4.

## Slide 4 — Análise em Malha Fechada sem Controlador (50 s)

Fechando a malha sem controlador (C(s)=1), calculamos G_MF(s) = 533,33 / (s² + 26,67s + 666,67). Daí tiramos wn = 25,82 rad/s e zeta = 0,5164, prevendo overshoot de 15%. Pelo Teorema do Valor Final, y(infinito) = 2,40 V para degrau de 3 V, logo erro de regime de 20%.

## Slide 5 — Simulação sem Controlador (45 s)

Integrando a planta com passo Δt = τ_min/100 = 0,5 ms, a simulação confirma exatamente as contas: erro de 20% (para em 2,40 V), overshoot de 15,24% e acomodação em 0,31 s.

## Slide 6 — Especificações e Método (45 s)

Defini quatro metas: erro zero, P.O. <= 5%, Ts <= 0,30 s e u entre 0 e 5 V. Escolhi a Segunda Maneira com o Método Polinomial: resolver a Equação Diofantina a(z)ℓ(z) + b(z)p(z) = a*(z) com modelo interno (z-1).

## Slide 7 — Discretização ZOH (1 min)

Aplicando a Equivalência do ZOH para h = τ_min/10 = 5 ms e expandindo G(s)/s em frações parciais, encontramos A=4, B=2 e C=-6. Aplicando a Transformada Z e multiplicando por (z-1)/z, obtemos G(z) exata.

## Slide 8 — Equação Diofantina (1 min 15 s)

Verificamos que a(z) e b(z) são coprimos. Impondo ℓ(z)=(z-1)ℓ₂(z), ã(z) fica de grau 3, então com a*(z) de grau 4 temos solução única causal com ℓ₂ de grau 1 e p de grau 2. Mapeando os polos -10 e -25 para z, montamos o sistema 4x4 igualando potências de z e chegamos ao controlador C(z).

## Slide 9 — Algoritmo e ZOH (45 s)

Dividindo numerador e denominador de C(z) por z² e aplicando Z inversa, temos a equação a diferenças causal. No algoritmo, a cada 5 ms lê y, calcula e = r - y, calcula u e mantém constante por 10 passos Δt pelo princípio do ZOH.

## Slide 10 — Simulação com Controlador (50 s)

Comparando com a curva sem controlador: erro caiu de 20% para zero, overshoot de 15,24% para 0,88%, Ts para 0,2565 s e controle entre 0,75 e 2,36 V. Todas as 4 metas foram atendidas.

## Slide 11 — Ajuste Fino (35 s)

Mostrando o ajuste fino: na 1ª tentativa com polos em -18 e -30, os zeros de p(z) causaram overshoot de 8,79% e pico de u em 7,23 V (acima de 5 V). Suavizando os polos para -10 e -25, todas as especificações ficaram dentro da meta.

## Slide 12 — Conclusões (30 s)

Concluindo: a análise teórica e a simulação bateram perfeitamente, o Método Polinomial zerou o erro e atendeu todas as metas com um algoritmo leve. O simulador completo está online no QR code. Obrigado!
