import numpy as np


# ============================================================
# TRANSFORMAÇÃO LINEAR
# ============================================================

A = np.array([
    [1, 0, 1],
    [0, 1, 1]
])

vetor = np.array([
    2,
    3,
    4
])

resultado = A @ vetor

print("===== TRANSFORMAÇÃO LINEAR =====")
print("Matriz A:")
print(A)

print("\nVetor:")
print(vetor)

print("\nA @ vetor:")
print(resultado)


# ============================================================
# TRANSFORMAÇÕES GEOMÉTRICAS
# ============================================================

v = np.array([
    2,
    1
])


escala = np.array([
    [2, 0],
    [0, 3]
])


reflexao = np.array([
    [1, 0],
    [0, -1]
])


rotacao_90 = np.array([
    [0, -1],
    [1, 0]
])


print("\n===== TRANSFORMAÇÕES GEOMÉTRICAS =====")

print("\nVetor original:")
print(v)

print("\nEscala:")
print(escala @ v)

print("\nReflexão:")
print(reflexao @ v)

print("\nRotação de 90 graus:")
print(rotacao_90 @ v)


# ============================================================
# MATRIZ DE INCIDÊNCIA
# ============================================================

M = np.array([
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [1, 1, 0, 0]
])


severidades = np.array([
    8,
    6,
    5,
    9
])


risco_proprio = M @ severidades


print("\n===== MODELO DE RISCO =====")

print("\nMatriz M:")
print(M)

print("\nVetor de severidades v:")
print(severidades)

print("\nRisco próprio b = Mv:")
print(risco_proprio)


# ============================================================
# MATRIZ DIAGONAL DE EXPOSIÇÃO
# ============================================================

F = np.diag([
    0.8,
    1.2,
    0.5
])


resultado_1 = F @ risco_proprio

FM = F @ M

resultado_2 = FM @ severidades


print("\n===== FATORES DE EXPOSIÇÃO =====")

print("\nMatriz F:")
print(F)

print("\nF(Mv):")
print(resultado_1)

print("\nMatriz FM:")
print(FM)

print("\n(FM)v:")
print(resultado_2)


# ============================================================
# VERIFICAÇÃO DA COMPOSIÇÃO
# ============================================================

print("\n===== VERIFICAÇÃO =====")

print(
    "F(Mv) = (FM)v ?",
    np.allclose(
        resultado_1,
        resultado_2
    )
)