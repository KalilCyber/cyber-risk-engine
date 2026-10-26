from interface.cli.menu_principal import MenuPrincipal
from servicos.inventario import Inventario
from servicos.servico_cve import ServicoCVE
from infraestrutura.persistencia_json import Persistencia

def main():

    repositorio = Persistencia()

    try:
        ativos_carregados = repositorio.carregar()

    except ValueError as erro:

        print(
            f"Erro ao carregar os dados: {erro}"
        )

        return


    inventario = Inventario(
        ativos_carregados,
        repositorio
    )


    # Cria o serviço responsável por consultar a NVD
    servico_cve = ServicoCVE()


    # Entrega as dependências para o Menu
    menu = MenuPrincipal(
        inventario,
        servico_cve
    )


    menu.executar()


if __name__ == "__main__":
    main()