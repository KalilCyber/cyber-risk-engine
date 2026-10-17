from persistencia import Persistencia
from inventario import Inventario
from modelo_risco import ModeloRisco


# ========================================================
# CARREGAR OS DADOS DO JSON
# ========================================================

persistencia = Persistencia()

ativos_carregados = (
    persistencia.carregar()
)


# ========================================================
# CRIAR O INVENTÁRIO
# ========================================================

inventario = Inventario(
    ativos_carregados
)


# ========================================================
# CRIAR O MODELO DE RISCO
# ========================================================

modelo = ModeloRisco(
    inventario
)


# ========================================================
# CALCULAR O RISCO PRÓPRIO
# ========================================================

vetor_b = (
    modelo.calcular_risco_proprio()
)


# ========================================================
# MOSTRAR OS ATIVOS
# ========================================================

print(
    "\n--- ATIVOS ---"
)

for indice, ativo in enumerate(
    modelo.ativos
):

    print(
        f"Linha {indice}: "
        f"ID {ativo.id} - "
        f"{ativo.nome}"
    )


# ========================================================
# MOSTRAR AS VULNERABILIDADES
# ========================================================

print(
    "\n--- VULNERABILIDADES ---"
)

for indice, vulnerabilidade in enumerate(
    modelo.vulnerabilidades
):

    print(
        f"Coluna {indice}: "
        f"{vulnerabilidade.obter_chave_modelo()} "
        f"| Severidade: "
        f"{vulnerabilidade.severidade}"
    )


# ========================================================
# MOSTRAR A MATRIZ M
# ========================================================

print(
    "\n--- MATRIZ M ---"
)

print(
    modelo.matriz_m
)


# ========================================================
# MOSTRAR O VETOR v
# ========================================================

print(
    "\n--- VETOR v ---"
)

print(
    modelo.vetor_v
)


# ========================================================
# MOSTRAR O VETOR b
# ========================================================

print(
    "\n--- RISCO PRÓPRIO b = Mv ---"
)

print(
    vetor_b
)