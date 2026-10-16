from menu import Menu
from inventario import Inventario
from persistencia import Persistencia
from servico_cve import ServicoCVE


def main():

    persistencia = Persistencia()

    try:
        ativos_carregados = persistencia.carregar()

    except ValueError as erro:

        print(
            f"Erro ao carregar os dados: {erro}"
        )

        return


    inventario = Inventario(
        ativos_carregados
    )


    # Cria o serviço responsável por consultar a NVD
    servico_cve = ServicoCVE()


    # Entrega as dependências para o Menu
    menu = Menu(
        inventario,
        persistencia,
        servico_cve
    )


    menu.executar()


if __name__ == "__main__":
    main()