# Roteiro da apresentação (≈ 9 min 30 s)

Simulador online: https://matteopeixotooo.github.io/Driver-LED-Project/

## Slide 1 — Capa (15 s)

Meu trabalho é o controle digital de iluminação: manter a luz de uma bancada num valor desejado usando um LED, um sensor de luz e um controlador digital. O QR code abre o simulador online do projeto.

## Slide 2 — A planta (50 s)

A planta é uma luminária de LED sobre uma bancada. O objetivo é manter a iluminação num valor, por exemplo 300 lux, que é o recomendado para escritórios. Um sensor de luz, o LDR, fica na bancada; o computador lê esse sensor e ajusta a tensão do LED. A entrada da planta é a tensão no driver do LED, de 0 a 5 V, e a saída é a tensão do sensor, calibrada para 1 V igual a 100 lux.

## Slide 3 — Componentes (50 s)

A planta tem dois blocos. O driver do LED transforma tensão em luz; ele tem um filtro RC que suaviza o PWM, então demora um pouco para responder: constante de tempo de 0,05 s, com ganho de 400 lux por volt. O sensor LDR transforma luz em tensão; somando a inércia do LDR com o filtro anti-ruído, a constante de tempo é 0,15 s, com 0,01 V por lux. A constante de tempo é o tempo de reação: em t = τ o bloco chega a 63 % do valor final. Dois blocos de primeira ordem em série dão uma planta de segunda ordem.

## Slide 4 — Modelagem (1 min)

Cada bloco é uma equação diferencial de primeira ordem. Aplicando Laplace e multiplicando os dois blocos, chego na função de transferência G(s) = 4 sobre (0,05s + 1)(0,15s + 1). O ganho 4 é 400 vezes 0,01. Em variáveis de estado, uso x1 = y e x2 = derivada de y, que é a forma que eu integro no computador com Runge-Kutta.

## Slide 5 — Análise da planta (40 s)

Analisando a planta sozinha: aplicando 0,75 V no LED, a saída vai para 3 V, porque o ganho é 4. Os polos são -20 e -6,67: reais e negativos, então é estável e não oscila. Mas é lenta, cerca de 0,63 s, e é tipo 0, sem integrador, o que já indica erro em regime quando fechar a malha.

## Slide 6 — Sem controlador (1 min)

Fechando a malha sem controlador, ou seja, u = r - y, com degrau de 3 V: aparecem três problemas. Erro em regime de 20 %: a luz para em 240 lux em vez de 300. Overshoot de 15 %: a luz passa do ponto e oscila. E leva 0,31 s para acomodar. Isso acontece porque a planta não tem integrador e a malha fechada fica subamortecida.

## Slide 7 — Especificações (40 s)

A partir disso defini quatro especificações: erro em regime zero, para a luz ficar exatamente no valor pedido; overshoot de no máximo 5 %, para não dar flash de luz; tempo de acomodação até 0,30 s, mais rápido que hoje; e sinal de controle entre 0 e 5 V, que é o limite físico do driver.

## Slide 8 — Método (1 min)

O enunciado permite duas maneiras. Na primeira projeta-se contínuo e depois discretiza o controlador. Eu usei a segunda: discretizo a planta e projeto o controlador direto no tempo discreto, que é exatamente o algoritmo que o computador executa. O método foi o Polinomial: eu escolho os polos da malha fechada e resolvo a equação a(z)ℓ(z) + b(z)p(z) = a*(z). Colocando o fator (z - 1) em ℓ(z) eu incluo um integrador, que garante erro zero.

## Slide 9 — Projeto (1 min)

Passo 1: a menor constante de tempo é 0,05 s, então pela regra do trabalho a planta é simulada com passo de 0,5 ms e o controlador amostra a cada 5 ms, ou seja, 10 passos da planta por amostra. Passo 2: discretizo a planta com o segurador de ordem zero e obtenho G(z). Passo 3: escolho os polos em -10, -10, -25 e -25 rad/s, resolvo o sistema e chego neste controlador C(z), que tem o integrador (z - 1) no denominador.

## Slide 10 — Algoritmo (30 s)

Este é o algoritmo: a cada 5 ms ele lê o sensor, calcula o erro, calcula u com a equação a diferenças e envia ao LED. Como pede o trabalho, u fica constante durante a amostra: cada degrau dura 10 passos da simulação da planta.

## Slide 11 — Com controlador (1 min)

Com o controlador, a curva azul é a nova resposta e a cinza é a antiga. O erro em regime foi de 20 % para zero, o overshoot de 15 % para 0,9 %, o tempo de acomodação de 0,31 para 0,26 s, e o sinal de controle ficou no máximo em 2,4 V, dentro do limite de 5 V. As quatro especificações foram atendidas.

## Slide 12 — Ajuste fino (30 s)

Esses polos vieram de um ajuste fino. Na primeira tentativa usei polos mais rápidos, -18 e -30: o overshoot foi 8,8 % e o sinal de controle passou de 7 V, acima do limite do driver. Suavizando para -10 e -25, tudo foi atendido.

## Slide 13 — Conclusão (20 s)

Resumindo: modelei a planta LED mais LDR como segunda ordem, sem controlador ela errava 20 % e oscilava, e com o controlador polinomial com integrador todas as metas foram atendidas. O simulador está online no QR code. Obrigado.
