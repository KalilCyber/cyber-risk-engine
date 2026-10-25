from infraestrutura.persistencia_json import Persistencia
from servicos.inventario import Inventario
from servicos.modelo_risco import ModeloRisco


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

matriz_a = (
    modelo.construir_matriz_a()
)


print(
    "\n--- MATRIZ A ---"
)

print(
    matriz_a
)


matriz_sistema = (
    modelo.construir_matriz_sistema()
)


print(
    "\n--- MATRIZ I - A ---"
)

print(
    matriz_sistema
)


vetor_x = (
    modelo.calcular_risco_efetivo()
)


print(
    "\n--- RISCO EFETIVO x ---"
)

print(
    vetor_x
)


print(
    "\n--- NÚMERO DE CONDIÇÃO ---"
)

print(
    modelo.numero_condicao
)