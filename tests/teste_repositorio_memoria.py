from dominio.ativos import Notebook
from infraestrutura.repositorio_memoria import RepositorioMemoria
from servicos.inventario import Inventario


# Cria o repositório em memória
repositorio = RepositorioMemoria()


# O mesmo Inventario recebe o repositório por injeção
inventario = Inventario(
    [],
    repositorio
)


# Cria um ativo apenas para o teste
notebook = Notebook(
    100,
    "Notebook Teste SOLID",
    "Kalil",
    "Cibersegurança",
    [],
    "Intel Core i5"
)


inventario.cadastrar_ativo(
    notebook
)


# Salva usando o próprio Inventario
inventario.salvar()


# Recupera diretamente do repositório em memória
ativos_carregados = (
    repositorio.carregar()
)


print(
    "\n--- TESTE REPOSITÓRIO EM MEMÓRIA ---"
)


for ativo in ativos_carregados:

    print(
        f"ID: {ativo.id}"
    )

    print(
        f"Nome: {ativo.nome}"
    )

    print(
        f"Tipo: {ativo.tipo}"
    )


print(
    "\nQuantidade de ativos carregados:",
    len(ativos_carregados)
)