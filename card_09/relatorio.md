# S3_09 — Álgebra Linear I: Matrizes e Transformações Lineares

## 1. Verificação de linearidade

Considere a transformação:

T(x, y) = (2x - y, 3y)

Para uma transformação ser linear, ela deve preservar soma e multiplicação por escalar.

Sejam:

u = (x1, y1)
v = (x2, y2)

Temos:

T(u + v)
= T(x1 + x2, y1 + y2)

= (2(x1 + x2) - (y1 + y2), 3(y1 + y2))

= (2x1 - y1, 3y1) + (2x2 - y2, 3y2)

= T(u) + T(v)

Para um escalar c:

T(cu)
= T(cx1, cy1)

= (2cx1 - cy1, 3cy1)

= c(2x1 - y1, 3y1)

= cT(u)

Logo, T é uma transformação linear.

Agora considere:

S(x, y) = (x + 1, y)

Temos:

S(0, 0) = (1, 0)

Como uma transformação linear deve satisfazer T(0) = 0, a função S não é linear.

---

## 2. Representação matricial de uma transformação

Considere:

T(x, y, z) = (x + z, y + z)

A transformação pode ser representada pela matriz:

A =

[ 1  0  1 ]
[ 0  1  1 ]

Assim:

T(v) = Av

A matriz possui dimensão 2 x 3.

Portanto:

T: R³ → R²

A transformação recebe um vetor com três componentes e produz um vetor com duas componentes.

---

## 3. Núcleo e imagem

Para determinar o núcleo da transformação, resolvemos:

Av = 0

Ou seja:

x + z = 0
y + z = 0

Logo:

x = -z
y = -z

Tomando z = t:

(x, y, z) = (-t, -t, t)

Portanto:

Ker(T) = span{(-1, -1, 1)}

O núcleo possui dimensão 1.

### Imagem

As colunas da matriz são:

c1 = (1, 0)
c2 = (0, 1)
c3 = (1, 1)

Os vetores c1 e c2 já formam uma base de R².

Logo:

Im(T) = R²

Portanto, a dimensão da imagem é 2.

---

## 4. Transformações geométricas

Considere o vetor:

v = (2, 1)

### Escala

Matriz:

D =

[ 2  0 ]
[ 0  3 ]

Aplicando:

Dv = (4, 3)

A transformação dobra a componente x e triplica a componente y.

### Reflexão em relação ao eixo x

R =

[ 1   0 ]
[ 0  -1 ]

Aplicando:

Rv = (2, -1)

A coordenada x permanece igual e o sinal da coordenada y é invertido.

### Rotação de 90 graus no sentido anti-horário

Q =

[ 0  -1 ]
[ 1   0 ]

Aplicando:

Qv = (-1, 2)

---

# 5. Aplicação ao modelo de risco

Considere três equipamentos:

- E1 — Notebook
- E2 — Servidor
- E3 — Roteador

E quatro vulnerabilidades:

- V1 — CVSS 8
- V2 — CVSS 6
- V3 — CVSS 5
- V4 — CVSS 9

O vetor de severidades é:

v =

[ 8 ]
[ 6 ]
[ 5 ]
[ 9 ]

A matriz de incidência equipamentos × vulnerabilidades será:

M =

[ 1  0  1  0 ]
[ 0  1  1  0 ]
[ 1  1  0  0 ]

Cada linha representa um equipamento.

Cada coluna representa uma vulnerabilidade.

O valor 1 indica que o equipamento é afetado pela vulnerabilidade e o valor 0 indica que não é afetado.

A matriz M possui dimensão 3 x 4.

Portanto:

M: R⁴ → R³

O vetor de severidades possui quatro valores e o resultado possui três valores, um para cada equipamento.

---

## 6. Cálculo manual do risco próprio

O risco próprio é calculado por:

b = Mv

Substituindo:

b =

[ 1  0  1  0 ]   [ 8 ]
[ 0  1  1  0 ] × [ 6 ]
[ 1  1  0  0 ]   [ 5 ]
                    [ 9 ]

### Equipamento E1

b1 = 1(8) + 0(6) + 1(5) + 0(9)

b1 = 13

### Equipamento E2

b2 = 0(8) + 1(6) + 1(5) + 0(9)

b2 = 11

### Equipamento E3

b3 = 1(8) + 1(6) + 0(5) + 0(9)

b3 = 14

Logo:

b =

[ 13 ]
[ 11 ]
[ 14 ]

Isso significa que, de acordo com o modelo utilizado, os riscos próprios dos equipamentos são:

- Notebook: 13
- Servidor: 11
- Roteador: 14

---

## 7. Interpretação de uma coluna nula

A quarta coluna da matriz M é:

[ 0 ]
[ 0 ]
[ 0 ]

Isso significa que a vulnerabilidade V4 não está associada a nenhum dos três equipamentos.

Mesmo possuindo severidade CVSS igual a 9, ela não contribui para o risco próprio de nenhum equipamento nesse cenário.

---

## 8. Núcleo da matriz de incidência

Para encontrar o núcleo de M, resolvemos:

Mv = 0

Considerando um vetor genérico:

v = (x1, x2, x3, x4)

Temos:

x1 + x3 = 0
x2 + x3 = 0
x1 + x2 = 0

Das duas primeiras equações:

x1 = -x3
x2 = -x3

Substituindo na terceira:

-x3 - x3 = 0

-2x3 = 0

x3 = 0

Logo:

x1 = 0
x2 = 0

A variável x4 é livre.

Portanto:

Ker(M) = span{(0, 0, 0, 1)}

Isso está de acordo com a interpretação da quarta coluna nula: qualquer severidade aplicada somente à vulnerabilidade V4 não altera o vetor de risco próprio.

---

## 9. Matriz diagonal de fatores de exposição

Considere fatores de exposição diferentes para cada equipamento:

F =

[ 0.8   0    0  ]
[  0   1.2   0  ]
[  0    0   0.5 ]

O vetor de risco próprio era:

b =

[ 13 ]
[ 11 ]
[ 14 ]

Aplicando os fatores:

Fb =

[ 0.8(13) ]
[ 1.2(11) ]
[ 0.5(14) ]

Logo:

Fb =

[ 10.4 ]
[ 13.2 ]
[ 7.0  ]

Como b = Mv:

F(Mv) = (FM)v

Portanto, a composição das duas transformações pode ser representada pelo produto das matrizes F e M.

A matriz:

FM =

[ 0.8   0    0.8   0 ]
[  0   1.2   1.2   0 ]
[ 0.5  0.5    0    0 ]

Aplicando novamente o vetor v:

(FM)v =

[ 10.4 ]
[ 13.2 ]
[ 7.0  ]

O resultado é igual a F(Mv), confirmando a propriedade de composição das transformações.

---

# Conclusão

As matrizes podem ser interpretadas como transformações lineares entre espaços vetoriais.

Uma matriz n x m representa uma transformação de R^m para R^n.

O núcleo representa os vetores que são transformados no vetor zero, enquanto a imagem representa os possíveis resultados da transformação.

No cenário de análise de risco, a matriz de incidência M transforma o vetor de severidades das vulnerabilidades em um vetor de risco próprio dos equipamentos por meio da expressão:

b = Mv

Também foi possível verificar que matrizes diagonais podem representar fatores de exposição e que a composição das transformações satisfaz:

F(Mv) = (FM)v

Os cálculos manuais foram conferidos utilizando Python e NumPy.