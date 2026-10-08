from inventario import Inventario
from persistencia import Persistencia


# Cria o objeto responsável pela persistência
persistencia = Persistencia()


# Carrega os ativos que já estão no JSON
ativos_carregados = persistencia.carregar()


# Cria o inventário utilizando os ativos carregados
inventario = Inventario(
    ativos_carregados
)


# Teste temporário da listagem
print("\n--- ATIVOS CADASTRADOS ---")


for ativo in inventario.listar_ativos():

    ativo.exibir_ativo()

    print("-" * 50)