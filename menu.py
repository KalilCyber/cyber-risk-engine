from ativos import Notebook, Servidor, Roteador, AplicacaoWeb


class Menu:

    def __init__(self, inventario, persistencia):
        self.inventario = inventario
        self.persistencia = persistencia


    # ========================================================
    # EXECUTAR MENU
    # ========================================================

    def executar(self):

        while True:

            print("\n===== CYBER RISK ENGINE =====")
            print("1 - Cadastrar ativo")
            print("2 - Listar ativos")
            print("3 - Consultar ativo")
            print("4 - Atualizar ativo")
            print("5 - Remover ativo")
            print("0 - Sair")

            opcao = input(
                "Escolha uma opção: "
            ).strip()


            if opcao == "1":
                self.cadastrar_ativo()

            elif opcao == "2":
                self.listar_ativos()

            elif opcao == "3":
                self.consultar_ativo()

            elif opcao == "4":
                self.atualizar_ativo()

            elif opcao == "5":
                self.remover_ativo()

            elif opcao == "0":
                print("Encerrando aplicação...")
                break

            else:
                print("Opção inválida.")


    # ========================================================
    # CADASTRAR ATIVO
    # ========================================================

    def cadastrar_ativo(self):

        print("\n--- CADASTRO DE ATIVO ---")

        try:

            id_ativo = int(
                input("ID do ativo: ")
            )

        except ValueError:

            print(
                "O ID deve ser um número inteiro."
            )

            return


        nome = input(
            "Nome/Hostname: "
        ).strip()

        responsavel = input(
            "Responsável: "
        ).strip()

        setor = input(
            "Setor: "
        ).strip()


        print("\nTipos disponíveis:")
        print("1 - Notebook")
        print("2 - Servidor")
        print("3 - Roteador")
        print("4 - Aplicação Web")


        tipo = input(
            "Escolha o tipo: "
        ).strip()


        if tipo == "1":

            processador = input(
                "Processador: "
            ).strip()

            ativo = Notebook(
                id_ativo,
                nome,
                responsavel,
                setor,
                [],
                processador
            )


        elif tipo == "2":

            servico = input(
                "Serviço: "
            ).strip()

            ativo = Servidor(
                id_ativo,
                nome,
                responsavel,
                setor,
                [],
                servico
            )


        elif tipo == "3":

            endereco_ip = input(
                "Endereço IP: "
            ).strip()

            ativo = Roteador(
                id_ativo,
                nome,
                responsavel,
                setor,
                [],
                endereco_ip
            )


        elif tipo == "4":

            ativo = AplicacaoWeb(
                id_ativo,
                nome,
                responsavel,
                setor,
                []
            )


        else:

            print(
                "Tipo de ativo inválido."
            )

            return


        try:

            self.inventario.cadastrar_ativo(
                ativo
            )

        except ValueError as erro:

            print(erro)

            return


        self.persistencia.salvar(
            self.inventario.listar_ativos()
        )


        print(
            "Ativo cadastrado com sucesso!"
        )


    # ========================================================
    # LISTAR ATIVOS
    # ========================================================

    def listar_ativos(self):

        ativos = (
            self.inventario.listar_ativos()
        )


        if not ativos:

            print(
                "\nNenhum ativo cadastrado."
            )

            return


        print(
            "\n--- ATIVOS CADASTRADOS ---"
        )


        for ativo in ativos:

            ativo.exibir_ativo()

            print("-" * 50)


    # ========================================================
    # CONSULTAR ATIVO
    # ========================================================

    def consultar_ativo(self):

        print(
            "\n--- CONSULTAR ATIVO ---"
        )

        print("1 - Buscar por ID")
        print("2 - Buscar por nome")


        opcao = input(
            "Escolha uma opção: "
        ).strip()


        # ----------------------------------------------------
        # BUSCA POR ID
        # ----------------------------------------------------

        if opcao == "1":

            try:

                id_ativo = int(
                    input("Digite o ID: ")
                )

            except ValueError:

                print(
                    "O ID deve ser um número inteiro."
                )

                return


            ativo = (
                self.inventario.buscar_por_id(
                    id_ativo
                )
            )


            if ativo is None:

                print(
                    "Ativo não encontrado."
                )

                return


            ativo.exibir_ativo()


        # ----------------------------------------------------
        # BUSCA POR NOME
        # ----------------------------------------------------

        elif opcao == "2":

            nome = input(
                "Digite o nome ou parte do nome: "
            ).strip()


            ativos = (
                self.inventario.buscar_por_nome(
                    nome
                )
            )


            if not ativos:

                print(
                    "Nenhum ativo encontrado."
                )

                return


            for ativo in ativos:

                ativo.exibir_ativo()

                print("-" * 50)


        else:

            print(
                "Opção de consulta inválida."
            )


    # ========================================================
    # ATUALIZAR ATIVO
    # ========================================================

    def atualizar_ativo(self):

        print(
            "\n--- ATUALIZAR ATIVO ---"
        )


        try:

            id_ativo = int(
                input(
                    "Digite o ID do ativo: "
                )
            )

        except ValueError:

            print(
                "O ID deve ser um número inteiro."
            )

            return


        ativo = (
            self.inventario.buscar_por_id(
                id_ativo
            )
        )


        if ativo is None:

            print(
                "Ativo não encontrado."
            )

            return


        print(
            "\nPressione ENTER para manter o valor atual."
        )


        nome = input(
            f"Nome [{ativo.nome}]: "
        ).strip()

        responsavel = input(
            f"Responsável [{ativo.responsavel}]: "
        ).strip()

        setor = input(
            f"Setor [{ativo.setor}]: "
        ).strip()


        if nome == "":
            nome = None

        if responsavel == "":
            responsavel = None

        if setor == "":
            setor = None


        atualizado = (
            self.inventario.atualizar_ativo(
                id_ativo,
                nome,
                responsavel,
                setor
            )
        )


        if atualizado:

            self.persistencia.salvar(
                self.inventario.listar_ativos()
            )

            print(
                "Ativo atualizado com sucesso!"
            )

        else:

            print(
                "Não foi possível atualizar o ativo."
            )


    # ========================================================
    # REMOVER ATIVO
    # ========================================================

    def remover_ativo(self):

        print(
            "\n--- REMOVER ATIVO ---"
        )


        try:

            id_ativo = int(
                input(
                    "Digite o ID do ativo: "
                )
            )

        except ValueError:

            print(
                "O ID deve ser um número inteiro."
            )

            return


        ativo = (
            self.inventario.buscar_por_id(
                id_ativo
            )
        )


        if ativo is None:

            print(
                "Ativo não encontrado."
            )

            return


        print(
            "\nAtivo encontrado:"
        )

        ativo.exibir_ativo()


        confirmacao = input(
            "\nDeseja realmente remover este ativo? (s/n): "
        ).strip().lower()


        if confirmacao != "s":

            print(
                "Remoção cancelada."
            )

            return


        removido = (
            self.inventario.remover_ativo(
                id_ativo
            )
        )


        if removido:

            self.persistencia.salvar(
                self.inventario.listar_ativos()
            )

            print(
                "Ativo removido com sucesso!"
            )

        else:

            print(
                "Não foi possível remover o ativo."
            )