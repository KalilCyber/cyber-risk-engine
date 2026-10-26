from interface.cli.menu_ativos import MenuAtivos
from interface.cli.menu_vulnerabilidades import MenuVulnerabilidades
from interface.cli.menu_risco import MenuRisco


class MenuPrincipal:

    def __init__(
        self,
        inventario,
        servico_cve
    ):

        self.menu_ativos = MenuAtivos(
            inventario
        )


        self.menu_vulnerabilidades = (
            MenuVulnerabilidades(
                inventario,
                servico_cve
            )
        )


        self.menu_risco = MenuRisco(
            inventario
        )


    def executar(self):

        while True:

            print(
                "\n===== CYBER RISK ENGINE ====="
            )

            print(
                "1 - Gerenciar ativos"
            )

            print(
                "2 - Gerenciar vulnerabilidades"
            )

            print(
                "3 - Análise de risco"
            )

            print(
                "0 - Sair"
            )


            opcao = input(
                "Escolha uma opção: "
            ).strip()


            if opcao == "1":

                self.menu_ativos.executar()


            elif opcao == "2":

                self.menu_vulnerabilidades.executar()


            elif opcao == "3":

                self.menu_risco.executar()


            elif opcao == "0":

                print(
                    "Encerrando aplicação..."
                )

                break


            else:

                print(
                    "Opção inválida."
                )