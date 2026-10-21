import numpy as np


# ============================================================
# SISTEMA 2x2
# ============================================================

A_2x2 = np.array([
    [1, 1],
    [2, -1]
], dtype=float)

b_2x2 = np.array([
    5,
    1
], dtype=float)

solucao_2x2 = np.linalg.solve(A_2x2, b_2x2)


print("===== SISTEMA 2x2 =====")

print("\nMatriz A:")
print(A_2x2)

print("\nVetor b:")
print(b_2x2)

print("\nSolução:")
print(solucao_2x2)


# ============================================================
# SISTEMA 3x3
# ============================================================

A_3x3 = np.array([
    [1, 1, 1],
    [2, -1, 1],
    [1, 2, -1]
], dtype=float)

b_3x3 = np.array([
    6,
    3,
    2
], dtype=float)

solucao_3x3 = np.linalg.solve(A_3x3, b_3x3)


print("\n===== SISTEMA 3x3 =====")

print("\nMatriz A:")
print(A_3x3)

print("\nVetor b:")
print(b_3x3)

print("\nSolução:")
print(solucao_3x3)


# ============================================================
# CLASSIFICAÇÃO DE SISTEMAS
# ============================================================

def classificar_sistema(A, b):
    """
    Classifica um sistema como:
    - possível determinado;
    - possível indeterminado;
    - impossível.
    """

    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    matriz_aumentada = np.column_stack((A, b))

    posto_A = np.linalg.matrix_rank(A)
    posto_aumentada = np.linalg.matrix_rank(matriz_aumentada)

    numero_incognitas = A.shape[1]

    if posto_A != posto_aumentada:
        return "Sistema impossível"

    if posto_A == numero_incognitas:
        return "Sistema possível determinado"

    return "Sistema possível indeterminado"


# Sistema possível determinado

A_determinado = [
    [1, 1],
    [2, -1]
]

b_determinado = [
    5,
    1
]


# Sistema possível indeterminado

A_indeterminado = [
    [1, 1],
    [2, 2]
]

b_indeterminado = [
    2,
    4
]


# Sistema impossível

A_impossivel = [
    [1, 1],
    [2, 2]
]

b_impossivel = [
    2,
    5
]


print("\n===== CLASSIFICAÇÃO DOS SISTEMAS =====")

print(
    "\nSistema 1:",
    classificar_sistema(
        A_determinado,
        b_determinado
    )
)

print(
    "Sistema 2:",
    classificar_sistema(
        A_indeterminado,
        b_indeterminado
    )
)

print(
    "Sistema 3:",
    classificar_sistema(
        A_impossivel,
        b_impossivel
    )
)


# ============================================================
# MODELO DE RISCO EFETIVO
# ============================================================

A_risco = np.array([
    [0, 0.5, 0],
    [0.5, 0, 0],
    [0, 0.5, 0]
], dtype=float)


b_risco = np.array([
    5,
    5,
    5
], dtype=float)


I = np.eye(3)

matriz_sistema = I - A_risco

risco_efetivo = np.linalg.solve(
    matriz_sistema,
    b_risco
)


print("\n===== MODELO DE RISCO EFETIVO =====")

print("\nMatriz de dependências A:")
print(A_risco)

print("\nMatriz identidade I:")
print(I)

print("\nMatriz do sistema I - A:")
print(matriz_sistema)

print("\nVetor de risco próprio b:")
print(b_risco)

print("\nRisco efetivo x:")
print(risco_efetivo)


# ============================================================
# VERIFICAÇÃO DA SOLUÇÃO
# ============================================================

lado_esquerdo = matriz_sistema @ risco_efetivo


print("\n===== VERIFICAÇÃO =====")

print("\n(I - A)x:")
print(lado_esquerdo)

print("\nb:")
print(b_risco)

print(
    "\n(I - A)x = b ?",
    np.allclose(
        lado_esquerdo,
        b_risco
    )
)