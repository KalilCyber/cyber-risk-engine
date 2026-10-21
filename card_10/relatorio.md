# S3_10 — Álgebra Linear II: Sistemas Lineares

## 1. Sistema linear 2×2

Considere o sistema:

x + y = 5

2x - y = 1

A matriz aumentada é:

[ 1   1 | 5 ]
[ 2  -1 | 1 ]

Aplicando eliminação de Gauss:

L2 ← L2 - 2L1

Temos:

[ 1   1 |  5 ]
[ 0  -3 | -9 ]

Da segunda linha:

-3y = -9

y = 3

Substituindo na primeira equação:

x + 3 = 5

x = 2

Logo:

x = 2
y = 3

O sistema possui uma única solução e, portanto, é um sistema possível determinado.

Geometricamente, as duas equações representam duas retas que se cruzam em um único ponto.

---

## 2. Sistema linear 3×3

Considere o sistema:

x + y + z = 6

2x - y + z = 3

x + 2y - z = 2

A matriz aumentada é:

[ 1   1   1 | 6 ]
[ 2  -1   1 | 3 ]
[ 1   2  -1 | 2 ]

Aplicamos:

L2 ← L2 - 2L1

L3 ← L3 - L1

Resultado:

[ 1   1   1 |  6 ]
[ 0  -3  -1 | -9 ]
[ 0   1  -2 | -4 ]

Trocando L2 com L3:

[ 1   1   1 |  6 ]
[ 0   1  -2 | -4 ]
[ 0  -3  -1 | -9 ]

Agora:

L3 ← L3 + 3L2

Temos:

[ 1   1   1 |   6 ]
[ 0   1  -2 |  -4 ]
[ 0   0  -7 | -21 ]

Da terceira linha:

-7z = -21

z = 3

Da segunda linha:

y - 2z = -4

y - 6 = -4

y = 2

Da primeira linha:

x + y + z = 6

x + 2 + 3 = 6

x = 1

Portanto:

x = 1
y = 2
z = 3

O sistema possui uma única solução.

---

# 3. Classificação de sistemas lineares

## 3.1 Sistema possível determinado

Considere:

x + y = 5

2x - y = 1

O sistema possui uma única solução:

(x, y) = (2, 3)

Logo, é um sistema possível determinado.

Geometricamente, as duas retas se cruzam em um único ponto.

---

## 3.2 Sistema possível indeterminado

Considere:

x + y = 2

2x + 2y = 4

A matriz aumentada é:

[ 1  1 | 2 ]
[ 2  2 | 4 ]

Aplicando:

L2 ← L2 - 2L1

Temos:

[ 1  1 | 2 ]
[ 0  0 | 0 ]

A segunda equação não acrescenta nenhuma nova informação.

Portanto, existem infinitas soluções.

Podemos escrever:

x = 2 - y

Como y pode assumir qualquer valor real, o sistema é possível indeterminado.

Geometricamente, as duas equações representam a mesma reta.

---

## 3.3 Sistema impossível

Considere:

x + y = 2

2x + 2y = 5

A matriz aumentada é:

[ 1  1 | 2 ]
[ 2  2 | 5 ]

Aplicando:

L2 ← L2 - 2L1

Obtemos:

[ 1  1 | 2 ]
[ 0  0 | 1 ]

A segunda linha representa:

0 = 1

Essa igualdade é impossível.

Portanto, o sistema não possui solução.

Geometricamente, as duas retas são paralelas e distintas.

---

# 4. Aplicação ao modelo de risco

Considere três equipamentos:

- E1 — Notebook
- E2 — Servidor
- E3 — Roteador

Considere que o risco próprio de cada equipamento é:

b =

[ 5 ]
[ 5 ]
[ 5 ]

A matriz de dependências entre os equipamentos será:

A =

[ 0    0.5   0   ]
[ 0.5   0    0   ]
[ 0    0.5   0   ]

A interpretação é:

- E1 recebe 50% do risco de E2;
- E2 recebe 50% do risco de E1;
- E3 recebe 50% do risco de E2.

O modelo de risco efetivo é:

x = b + Ax

onde:

x = vetor de risco efetivo;

b = vetor de risco próprio;

A = matriz de dependências.

---

# 5. Reorganização do sistema

Partindo de:

x = b + Ax

Subtraímos Ax dos dois lados:

x - Ax = b

Como:

x = Ix

podemos escrever:

Ix - Ax = b

Colocando x em evidência:

(I - A)x = b

A matriz identidade é:

I =

[ 1  0  0 ]
[ 0  1  0 ]
[ 0  0  1 ]

Logo:

I - A =

[ 1    -0.5   0   ]
[ -0.5  1     0   ]
[ 0    -0.5   1   ]

O sistema matricial é:

[ 1    -0.5   0   ]   [ x1 ]   [ 5 ]
[ -0.5  1     0   ] × [ x2 ] = [ 5 ]
[ 0    -0.5   1   ]   [ x3 ]   [ 5 ]

Isso gera as equações:

x1 - 0.5x2 = 5

-0.5x1 + x2 = 5

-0.5x2 + x3 = 5

---

# 6. Resolução manual por eliminação de Gauss

A matriz aumentada é:

[ 1    -0.5   0 | 5 ]
[ -0.5  1     0 | 5 ]
[ 0    -0.5   1 | 5 ]

Aplicamos:

L2 ← L2 + 0.5L1

Temos:

[ 1  -0.5   0 | 5   ]
[ 0   0.75  0 | 7.5 ]
[ 0  -0.5   1 | 5   ]

Agora eliminamos o valor -0.5 da terceira linha.

Como:

0.5 / 0.75 = 2/3

aplicamos:

L3 ← L3 + (2/3)L2

Resultado:

[ 1  -0.5   0 | 5   ]
[ 0   0.75  0 | 7.5 ]
[ 0    0     1 | 10  ]

Agora fazemos a retrossubstituição.

Da terceira linha:

x3 = 10

Da segunda linha:

0.75x2 = 7.5

x2 = 10

Da primeira linha:

x1 - 0.5(10) = 5

x1 - 5 = 5

x1 = 10

Portanto:

x =

[ 10 ]
[ 10 ]
[ 10 ]

---

# 7. Interpretação do resultado

O vetor de risco próprio era:

b =

[ 5 ]
[ 5 ]
[ 5 ]

Após considerar as dependências entre os equipamentos, o vetor de risco efetivo passou a ser:

x =

[ 10 ]
[ 10 ]
[ 10 ]

Isso mostra que as dependências entre os equipamentos podem aumentar o risco efetivo.

Cada equipamento possui seu próprio risco, mas também recebe uma parcela do risco dos equipamentos dos quais depende.

No cenário analisado:

- E1 possui risco efetivo 10;
- E2 possui risco efetivo 10;
- E3 possui risco efetivo 10.

O sistema possui uma única solução.

Geometricamente, em um sistema de três variáveis, cada equação pode ser interpretada como um plano em R³. Nesse caso, os três planos possuem um ponto de interseção comum correspondente a:

(10, 10, 10)

---

# 8. Validação com Python e NumPy

A solução também pode ser obtida computacionalmente usando:

numpy.linalg.solve()

Para resolver:

(I - A)x = b

utilizamos diretamente:

x = np.linalg.solve(I - A, b)

O resultado obtido é:

x = [10, 10, 10]

O resultado computacional confirma a resolução manual realizada por eliminação de Gauss.

---

# Conclusão

Os sistemas de equações lineares podem ser representados na forma matricial:

Ax = b

A eliminação de Gauss permite transformar um sistema em uma forma escalonada para posteriormente encontrar suas incógnitas por retrossubstituição.

Um sistema linear pode ser classificado como:

- possível determinado, quando possui uma única solução;
- possível indeterminado, quando possui infinitas soluções;
- impossível, quando não possui solução.

No modelo de análise de risco, a equação:

x = b + Ax

pode ser reorganizada como:

(I - A)x = b

Essa representação permite calcular o risco efetivo dos equipamentos considerando tanto o risco próprio quanto o risco transmitido pelas dependências.

No cenário estudado, o sistema foi resolvido manualmente por eliminação de Gauss e posteriormente validado utilizando Python e NumPy.