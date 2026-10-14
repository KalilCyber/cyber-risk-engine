from ativos import Notebook, Servidor, Roteador, AplicacaoWeb
from vulnerabilidades import Vulnerabilidade
from enums import Tratamento


class Menu:

    def __init__(self, inventario, persistencia):
        self.inventario = inventario
        self.persistencia = persistencia
    
    def ler_campo_obrigatorio(self, mensagem):

        while True:
            valor = input(mensagem).strip()
            if valor:
                return valor
            
            print("Este campo não pode ficar vazio.")

    def ler_responsavel(self, mensagem, permitir_vazio=False):

        while True:
            responsavel = input(mensagem).strip()

            if permitir_vazio and responsavel == "":
                return None
            
            if (responsavel and responsavel.replace(" ", "").isalpha()):
                return responsavel
            
            print("Responsável inválido."
                  "Digite apenas letras e espaços.")
            
            

    # EXECUTAR MENU

    def executar(self):

        while True:

            print("\n===== CYBER RISK ENGINE =====")
            print("1 - Cadastrar ativo")
            print("2 - Listar ativos")
            print("3 - Consultar ativo")
            print("4 - Atualizar ativo")
            print("5 - Remover ativo")
            print("6 - Cadastrar vulnerabilidade")
            print("7 - Listar vulnerabilidades de um ativo")
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

            elif opcao == "6":
                self.cadastrar_vulnerabilidade()

            elif opcao == "7":
                self.listar_vulnerabilidades()

            elif opcao == "0":
                print("Encerrando aplicação...")
                break

            else:
                print("Opção inválida.")

    # CADASTRAR ATIVO

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


        nome = self.ler_campo_obrigatorio("Nome/Hostname:")

        responsavel = self.ler_responsavel("Responsável:")

        setor = self. ler_campo_obrigatorio("Setor:")


        print("\nTipos disponíveis:")
        print("1 - Notebook")
        print("2 - Servidor")
        print("3 - Roteador")
        print("4 - Aplicação Web")


        tipo = input(
            "Escolha o tipo: "
        ).strip()


        if tipo == "1":

            processador = self.ler_campo_obrigatorio("Processador: ")
        
            ativo = Notebook(
                id_ativo,
                nome,
                responsavel,
                setor,
                [],
                processador
            )


        elif tipo == "2":

            servico = self.ler_campo_obrigatorio("Serviço: ")

            ativo = Servidor(
                id_ativo,
                nome,
                responsavel,
                setor,
                [],
                servico
            )


        elif tipo == "3":

            endereco_ip = self.ler_campo_obrigatorio("Endereço IP: ")

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


    # LISTAR ATIVOS

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


    # CONSULTAR ATIVO

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


    
    # ATUALIZAR ATIVO
   

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

        responsavel = self.ler_responsavel(
            f"Responsável [{ativo.responsavel}]: ",
            permitir_vazio=True)

        setor = input(
            f"Setor [{ativo.setor}]: "
        ).strip()


        if nome == "":
            nome = None

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

    
    # REMOVER ATIVO

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

    
    # CADASTRAR VULNERABILIDADE

    def cadastrar_vulnerabilidade(self):

        print("\n--- CADASTRAR VULNERABILIDADE ---")

        try:
            id_ativo = int(
                input("ID do ativo: ")
            )

        except ValueError:
            print("O ID do ativo deve ser um número inteiro.")
            return


        ativo = self.inventario.buscar_por_id(
            id_ativo
        )

        if ativo is None:
            print("Ativo não encontrado.")
            return


        try:
            id_vulnerabilidade = int(
                input("ID da vulnerabilidade: ")
            )

        except ValueError:
            print(
                "O ID da vulnerabilidade deve ser um número inteiro."
            )
            return


        descricao = self.ler_campo_obrigatorio("Descrição: ")

        categoria = self.ler_campo_obrigatorio("Categoria: ")


        try:
            severidade = float(
                input("Severidade (0 a 10): ")
            )

        except ValueError:
            print(
                "A severidade deve ser um número."
            )
            return


        print("\nStatus disponíveis:")

        for tratamento in Tratamento:
            print(
                f"{tratamento.value} - {tratamento.name}"
            )

        try:
            codigo_status = int(
                input("Escolha o status: ")
            )

            status = Tratamento(codigo_status)

        except ValueError:
            print("Status inválido.")
            return

        try:

            vulnerabilidade = Vulnerabilidade(
                id_vulnerabilidade,
                descricao,
                categoria,
                severidade,
                status
            )

        except ValueError as erro:

            print(erro)
            return

        try:

            adicionada = (
                self.inventario.associar_vulnerabilidade(
                    id_ativo,
                    vulnerabilidade
                )
            )

        except ValueError as erro:

            print(erro)
            return


        if not adicionada:
            print(
                "Não foi possível adicionar a vulnerabilidade."
            )
            return


        self.persistencia.salvar(
            self.inventario.listar_ativos()
        )


        print(
            "Vulnerabilidade cadastrada com sucesso!"
        )

        # ========================================================
    # LISTAR VULNERABILIDADES
    # ========================================================

    def listar_vulnerabilidades(self):

        print(
            "\n--- VULNERABILIDADES DO ATIVO ---"
        )


        try:
            id_ativo = int(
                input("ID do ativo: ")
            )

        except ValueError:
            print(
                "O ID deve ser um número inteiro."
            )
            return


        vulnerabilidades = (
            self.inventario.listar_vulnerabilidades(
                id_ativo
            )
        )


        if vulnerabilidades is None:

            print("Ativo não encontrado.")
            return


        if not vulnerabilidades:

            print(
                "Nenhuma vulnerabilidade cadastrada para este ativo."
            )
            return


        for vulnerabilidade in vulnerabilidades:

            vulnerabilidade.exibir_vulnerabilidade()

            print("-" * 50)