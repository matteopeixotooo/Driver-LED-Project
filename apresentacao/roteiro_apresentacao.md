# Roteiro da apresentação (≈ 9 min)
Fale com calma; o tempo entre parênteses é uma referência.

## Slide 1 — Capa (20 s)

Bom dia. Meu trabalho é o controle digital de um sistema de iluminação: um driver de LED e um sensor LDR, controlados por um controlador digital que eu projetei pelo Método Polinomial.

## Slide 2 — A planta (1 min)

A planta é uma luminária de LED iluminando uma bancada. A entrada é a tensão no driver, de 0 a 5 V. O driver transforma tensão em luz, com constante de tempo de 0,05 s. O sensor LDR mede essa luz e devolve uma tensão, com constante de tempo de 0,15 s, calibrado para 1 V igual a 100 lux. O objetivo é manter a luz na bancada no valor desejado, por exemplo 300 lux.

## Slide 3 — Modelagem (1 min 15 s)

Cada bloco é modelado por uma equação diferencial de primeira ordem. Aplicando Laplace e juntando os dois, cheguei na função de transferência G(s) = 4 / [(0,05s + 1)(0,15s + 1)]. Na forma de variáveis de estado, uso x1 = y e x2 = derivada de y, que é o que eu integro na simulação. É uma planta de 2ª ordem, estável, com polos em −20 e −6,67, e do tipo 0, sem integrador. Por isso já dá para esperar erro em regime na malha fechada.

## Slide 4 — Malha fechada sem controlador (1 min 15 s)

Simulando em malha fechada sem controlador, ou seja, u = r − y, com degrau de 3 V: aparecem três problemas. Primeiro, erro em regime de 20 %: a saída para em 2,4 V. Segundo, overshoot de 15 %: a luz passa do ponto e oscila. Terceiro, leva 0,31 s para acomodar.

## Slide 5 — Especificações e método (1 min 15 s)

Então defini as especificações: erro em regime zero, overshoot de no máximo 5 %, tempo de acomodação de até 0,30 s e sinal de controle entre 0 e 5 V, que é o limite do driver. Projetei um controlador digital de 2ª ordem com ação integral pelo Método Polinomial. Embaixo está a malha: o computador calcula C(z) a cada 5 ms, o ZOH segura o valor e aplica na planta.

## Slide 6 — Projeto pelo Método Polinomial (1 min 30 s)

O projeto teve três passos. Um: a menor constante de tempo é 0,05 s, então pela regra do trabalho a amostragem é h = τmin/10 = 5 ms, e a planta é simulada com passo de 0,5 ms. Dois: discretizei a planta pelo ZOH e obtive G(z). Três: resolvi a Equação Diofantina. Coloquei o fator (z − 1) em ℓ(z), que é o integrador e garante erro zero ao degrau, e escolhi os polos desejados em −10, −10, −25 e −25. Resolvendo, chego nesse controlador C(z).

## Slide 7 — Malha fechada com controlador (1 min 30 s)

Com o controlador, a curva azul é a nova resposta e a cinza é a antiga, sem controlador. O erro em regime foi de 20 % para zero, o overshoot de 15 % para 0,9 %, o tempo de acomodação de 0,31 para 0,26 s, e o sinal de controle ficou no máximo em 2,4 V, dentro do limite de 5 V. Ou seja, as quatro especificações foram atendidas.

## Slide 8 — Conclusão (45 s)

Para fechar, testei mudando a referência para 200, 400 e 300 lux, e o controlador segue todos os degraus sem erro. Resumindo: sem controlador havia erro de 20 % e oscilação; com o Método Polinomial e o integrador, o erro foi a zero e a resposta ficou rápida e sem oscilação. Obrigado.

## Extra — Apêndice A — Algoritmo (só se perguntarem)

Este é o algoritmo: a cada 5 ms lê o sensor, calcula o erro, calcula u com a equação a diferenças, atualiza as variáveis passadas e envia u para o driver.

## Extra — Apêndice B — Ajuste dos polos (só se perguntarem)

Na primeira tentativa usei polos mais rápidos, −18 e −30. O erro zerou, mas o overshoot foi 8,8 % e o sinal de controle passou de 7 V, acima do limite de 5 V. Suavizei os polos para −10 e −25 e todas as especificações foram atendidas.
