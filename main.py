from menu import Menu
from servicos.inventario import Inventario
from servicos.servico_cve import ServicoCVE
from infraestrutura.persistencia_json import Persistencia

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