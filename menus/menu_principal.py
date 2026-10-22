from menus.menu_ativos import MenuAtivos
from menus.menu_vulnerabilidades import MenuVulnerabilidades
from menus.menu_risco import MenuRisco


class MenuPrincipal:

    def __init__(
        self,
        inventario,
        persistencia,
        servico_cve
    ):

        self.menu_ativos = MenuAtivos(
            inventario,
            persistencia
        )


        self.menu_vulnerabilidades = (
            MenuVulnerabilidades(
                inventario,
                persistencia,
                servico_cve
            )
        )


        self.menu_risco = MenuRisco(
            inventario,
            persistencia
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