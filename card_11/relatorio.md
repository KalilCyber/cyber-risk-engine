# S3_11 — Álgebra Linear III: Determinantes e Invertibilidade

## 1. Determinante e inversa de uma matriz 2×2

Considere a matriz:

A =

[ 2  1 ]
[ 1  1 ]

Para uma matriz 2×2:

[ a  b ]
[ c  d ]

o determinante é calculado por:

det(A) = ad - bc

Portanto:

det(A) = 2(1) - 1(1)

det(A) = 2 - 1

det(A) = 1

Como:

det(A) ≠ 0

a matriz A é invertível.

---

## 2. Cálculo da matriz inversa

Para uma matriz 2×2:

A =

[ a  b ]
[ c  d ]

a inversa é:

A⁻¹ = 1/det(A) ×

[  d  -b ]
[ -c   a ]

Como det(A) = 1:

A⁻¹ =

[  1  -1 ]
[ -1   2 ]

Agora verificamos o produto:

AA⁻¹ =

[ 2  1 ] [  1  -1 ]
[ 1  1 ] [ -1   2 ]

Calculando:

AA⁻¹ =

[ 2(1) + 1(-1)     2(-1) + 1(2) ]
[ 1(1) + 1(-1)     1(-1) + 1(2) ]

AA⁻¹ =

[ 1  0 ]
[ 0  1 ]

Logo:

AA⁻¹ = I

Portanto, a matriz inversa está correta.

---

# 3. Determinante de uma matriz 3×3

Considere:

B =

[ 1  2  3 ]
[ 0  1  4 ]
[ 5  6  0 ]

## 3.1 Regra de Sarrus

A regra de Sarrus pode ser utilizada apenas em matrizes 3×3.

Calculando as diagonais positivas:

1 × 1 × 0 = 0

2 × 4 × 5 = 40

3 × 0 × 6 = 0

Soma positiva:

0 + 40 + 0 = 40

Calculando as diagonais negativas:

3 × 1 × 5 = 15

2 × 0 × 0 = 0

1 × 4 × 6 = 24

Soma negativa:

15 + 0 + 24 = 39

Portanto:

det(B) = 40 - 39

det(B) = 1

Como o determinante é diferente de zero, B é invertível.

---

## 3.2 Expansão por cofatores

Utilizando a primeira linha:

det(B) =

1 × det([1 4; 6 0])
- 2 × det([0 4; 5 0])
+ 3 × det([0 1; 5 6])

Calculando:

det(B) =

1(1×0 - 4×6)
- 2(0×0 - 4×5)
+ 3(0×6 - 1×5)

det(B) =

-24 + 40 - 15

det(B) = 1

O resultado é igual ao obtido pela regra de Sarrus.

---

# 4. Exemplo de matriz singular

Considere:

C =

[ 1  2  3 ]
[ 2  4  6 ]
[ 1  0  1 ]

A segunda linha é exatamente duas vezes a primeira.

Portanto, as linhas são linearmente dependentes.

Calculando o determinante:

det(C) = 0

Uma matriz cujo determinante é zero é chamada de matriz singular.

Logo:

C não possui matriz inversa.

---

# 5. Significado geométrico do determinante

O determinante também possui uma interpretação geométrica.

## Matrizes 2×2

Em uma transformação linear no plano, o valor absoluto do determinante indica o fator pelo qual as áreas são multiplicadas.

Por exemplo:

det(A) = 2

significa que uma área após a transformação será duas vezes maior que a área original.

Se:

det(A) = -2

o fator de área continua sendo 2, mas o sinal negativo indica que ocorreu uma inversão de orientação.

Se:

det(A) = 0

a área é reduzida a zero.

Nesse caso, a transformação comprime o plano para uma dimensão menor e a matriz não é invertível.

---

## Matrizes 3×3

Para uma transformação em R³, o valor absoluto do determinante representa o fator de escala do volume.

Por exemplo:

|det(A)| = 3

significa que o volume é multiplicado por 3.

Se:

det(A) = 0

o volume é reduzido a zero, indicando perda de dimensão.

---

# 6. Relação entre determinante, inversa e sistemas lineares

Considere o sistema:

Ax = b

Se:

det(A) ≠ 0

então A possui inversa.

Nesse caso:

x = A⁻¹b

e o sistema possui uma única solução.

Por outro lado, se:

det(A) = 0

a matriz é singular e não possui inversa.

Nesse caso, o sistema pode:

- não possuir solução;
- possuir infinitas soluções.

Portanto, uma matriz singular não garante uma solução única.

---

# 7. Aplicação ao modelo de risco — cenário invertível

No modelo de risco efetivo:

x = b + Ax

Reorganizando:

(I - A)x = b

Para que seja possível obter uma única solução para o risco efetivo, a matriz:

I - A

deve ser invertível.

Considere a matriz de dependências:

A =

[ 0    0.2  0.1 ]
[ 0.1  0    0.2 ]
[ 0.1  0.1  0   ]

A matriz identidade é:

I =

[ 1  0  0 ]
[ 0  1  0 ]
[ 0  0  1 ]

Portanto:

I - A =

[ 1    -0.2  -0.1 ]
[ -0.1  1    -0.2 ]
[ -0.1 -0.1   1   ]

---

# 8. Dominância diagonal estrita

Uma matriz é estritamente diagonal dominante quando, em cada linha, o valor absoluto do elemento da diagonal é maior que a soma dos valores absolutos dos demais elementos da mesma linha.

Na primeira linha:

|1| > |-0.2| + |-0.1|

1 > 0.3

Na segunda linha:

1 > 0.1 + 0.2

1 > 0.3

Na terceira linha:

1 > 0.1 + 0.1

1 > 0.2

Portanto, I - A é estritamente diagonal dominante.

Uma matriz estritamente diagonal dominante é não singular.

Logo:

I - A é invertível.

Consequentemente, o sistema:

(I - A)x = b

possui uma única solução para qualquer vetor b.

---

# 9. Relação com a soma das linhas de A

No modelo utilizado, os elementos de A representam pesos de dependência e são não negativos.

Se a soma de cada linha de A for menor que 1:

Σ Aij < 1

então, em I - A, o elemento da diagonal possui valor 1 enquanto a soma dos valores absolutos dos elementos fora da diagonal é menor que 1.

Assim:

|1| > Σ |Aij|

Portanto, I - A é estritamente diagonal dominante.

Isso fornece um critério suficiente para garantir sua invertibilidade.

---

# 10. Cenário singular do modelo de risco

Agora considere:

A =

[ 0    0.5  0.5 ]
[ 0.5  0    0.5 ]
[ 0.5  0.5  0   ]

Todos os pesos individualmente pertencem ao intervalo:

0 ≤ peso < 1

Porém, a soma de cada linha é:

0.5 + 0.5 = 1

Agora:

I - A =

[ 1    -0.5  -0.5 ]
[ -0.5  1    -0.5 ]
[ -0.5 -0.5   1   ]

Calculando seu determinante:

det(I - A) = 0

Portanto:

I - A

é uma matriz singular.

Ela não possui inversa.

Isso significa que o sistema de risco:

(I - A)x = b

não possui garantia de solução única.

Dependendo do vetor b, o sistema poderá ter infinitas soluções ou nenhuma solução.

No contexto do modelo de risco, isso significa que as dependências entre os equipamentos formaram uma estrutura forte o suficiente para impedir a determinação de um único vetor de risco efetivo.

Esse cenário mostra a importância de validar I - A antes de tentar resolver o sistema.

---

# 11. Comparação dos dois cenários

## Cenário 1 — Invertível

A =

[ 0    0.2  0.1 ]
[ 0.1  0    0.2 ]
[ 0.1  0.1  0   ]

As somas das linhas são:

Linha 1 = 0.3

Linha 2 = 0.3

Linha 3 = 0.2

Todas são menores que 1.

Assim, I - A é estritamente diagonal dominante e invertível.

O sistema possui solução única.

---

## Cenário 2 — Singular

A =

[ 0    0.5  0.5 ]
[ 0.5  0    0.5 ]
[ 0.5  0.5  0   ]

As somas das linhas são:

Linha 1 = 1

Linha 2 = 1

Linha 3 = 1

Nesse caso, não existe dominância diagonal estrita.

Além disso:

det(I - A) = 0

Logo, I - A é singular.

O sistema não possui uma solução única garantida.

---

# Conclusão

O determinante permite identificar se uma matriz quadrada é invertível.

Se:

det(A) ≠ 0

a matriz é invertível e um sistema Ax = b possui solução única.

Se:

det(A) = 0

a matriz é singular e não possui inversa.

Também foi observado que o valor absoluto do determinante representa o fator de escala de áreas em R² e volumes em R³.

No modelo de risco, é necessário analisar a matriz:

I - A

antes de resolver:

(I - A)x = b

Se a soma de cada linha da matriz de dependências A for menor que 1, então I - A é estritamente diagonal dominante, o que garante sua invertibilidade.

Os cálculos foram posteriormente conferidos utilizando Python e NumPy.