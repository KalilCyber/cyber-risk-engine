import numpy as np


# ============================================================
# MATRIZ 2x2 — DETERMINANTE E INVERSA
# ============================================================

A = np.array([
    [2, 1],
    [1, 1]
], dtype=float)


det_A = np.linalg.det(A)

inversa_A = np.linalg.inv(A)

produto_identidade = A @ inversa_A


print("===== MATRIZ 2x2 =====")

print("\nMatriz A:")
print(A)

print("\nDeterminante:")
print(det_A)

print("\nMatriz inversa:")
print(inversa_A)

print("\nA @ A^-1:")
print(produto_identidade)

print(
    "\nProduto é identidade?",
    np.allclose(
        produto_identidade,
        np.eye(2)
    )
)


# ============================================================
# MATRIZ 3x3
# ============================================================

B = np.array([
    [1, 2, 3],
    [0, 1, 4],
    [5, 6, 0]
], dtype=float)


det_B = np.linalg.det(B)


print("\n===== MATRIZ 3x3 =====")

print("\nMatriz B:")
print(B)

print("\nDeterminante de B:")
print(det_B)


# ============================================================
# MATRIZ SINGULAR
# ============================================================

C = np.array([
    [1, 2, 3],
    [2, 4, 6],
    [1, 0, 1]
], dtype=float)


det_C = np.linalg.det(C)


print("\n===== MATRIZ SINGULAR =====")

print("\nMatriz C:")
print(C)

print("\nDeterminante de C:")
print(det_C)

print(
    "\nC é singular?",
    np.isclose(det_C, 0)
)


# ============================================================
# MODELO DE RISCO — CENÁRIO INVERTÍVEL
# ============================================================

A_risco_invertivel = np.array([
    [0, 0.2, 0.1],
    [0.1, 0, 0.2],
    [0.1, 0.1, 0]
], dtype=float)


I = np.eye(3)

matriz_invertivel = I - A_risco_invertivel

det_invertivel = np.linalg.det(
    matriz_invertivel
)


print("\n===== CENÁRIO DE RISCO INVERTÍVEL =====")

print("\nMatriz A:")
print(A_risco_invertivel)

print("\nI - A:")
print(matriz_invertivel)

print("\nDeterminante de I - A:")
print(det_invertivel)

print(
    "\nI - A é invertível?",
    not np.isclose(det_invertivel, 0)
)


# ============================================================
# VERIFICAÇÃO DA DOMINÂNCIA DIAGONAL
# ============================================================

def diagonalmente_dominante(matriz):
    for i in range(len(matriz)):
        diagonal = abs(matriz[i, i])

        soma_fora_diagonal = (
            np.sum(np.abs(matriz[i]))
            - diagonal
        )

        if diagonal <= soma_fora_diagonal:
            return False

    return True


print(
    "\nEstritamente diagonal dominante?",
    diagonalmente_dominante(
        matriz_invertivel
    )
)


# ============================================================
# RESOLUÇÃO DO CENÁRIO INVERTÍVEL
# ============================================================

b = np.array([
    5,
    5,
    5
], dtype=float)


x = np.linalg.solve(
    matriz_invertivel,
    b
)


print("\nVetor de risco próprio b:")
print(b)

print("\nVetor de risco efetivo x:")
print(x)

print(
    "\nSolução correta?",
    np.allclose(
        matriz_invertivel @ x,
        b
    )
)


# ============================================================
# MODELO DE RISCO — CENÁRIO SINGULAR
# ============================================================

A_risco_singular = np.array([
    [0, 0.5, 0.5],
    [0.5, 0, 0.5],
    [0.5, 0.5, 0]
], dtype=float)


matriz_singular = I - A_risco_singular

det_risco_singular = np.linalg.det(
    matriz_singular
)


print("\n===== CENÁRIO DE RISCO SINGULAR =====")

print("\nMatriz A:")
print(A_risco_singular)

print("\nI - A:")
print(matriz_singular)

print("\nDeterminante de I - A:")
print(det_risco_singular)

print(
    "\nI - A é singular?",
    np.isclose(
        det_risco_singular,
        0
    )
)

print(
    "\nEstritamente diagonal dominante?",
    diagonalmente_dominante(
        matriz_singular
    )
)


# ============================================================
# TENTATIVA DE INVERSÃO
# ============================================================

print("\n===== TENTATIVA DE INVERSÃO =====")

try:
    inversa_singular = np.linalg.inv(
        matriz_singular
    )

    print(inversa_singular)

except np.linalg.LinAlgError:

    print(
        "A matriz é singular e não possui inversa."
    )