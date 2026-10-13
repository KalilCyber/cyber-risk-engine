from menu import Menu
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


menu = Menu(
    inventario,
    persistencia
)

menu.executar()
