from ativos import (
    Notebook,
    Servidor,
    Roteador,
    AplicacaoWeb
)

from menus.menu_base import MenuBase
from enums import Tratamento


class MenuAtivos(MenuBase):

    def executar(self):

        while True:

            print(
                "\n===== GERENCIAR ATIVOS ====="
            )

            print(
                "1 - Cadastrar ativo"
            )

            print(
                "2 - Listar ativos"
            )

            print(
                "3 - Consultar ativo"
            )

            print(
                "4 - Atualizar ativo"
            )

            print(
                "5 - Remover ativo"
            )

            print(
                "0 - Voltar"
            )


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

                break


            else:

                print(
                    "Opção inválida."
                )


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

            url = self.ler_campo_obrigatorio("URL: ")
            "URL da aplicação web: "

            ativo = AplicacaoWeb(
                id_ativo, nome, responsavel, setor, [], url)


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


        ativo = self.inventario.buscar_por_id(
            id_ativo
        )


        if ativo is None:

            print(
                "Ativo não encontrado."
            )

            return


        print(
            "\nPressione ENTER para manter o valor atual."
        )

   # CAMPOS COMUNS
  
        nome = input(
            f"Nome [{ativo.nome}]: "
        ).strip()


        responsavel = self.ler_responsavel(
            f"Responsável [{ativo.responsavel}]: ",
            permitir_vazio=True
        )


        setor = input(
            f"Setor [{ativo.setor}]: "
        ).strip()


        
        # ATRIBUTO ESPECÍFICO

        atributo_especifico = None


        if isinstance(ativo, Notebook):

            atributo_especifico = input(
                f"Processador [{ativo.processador}]: "
            ).strip()


        elif isinstance(ativo, Servidor):

            atributo_especifico = input(
                f"Serviço [{ativo.servico}]: "
            ).strip()


        elif isinstance(ativo, Roteador):

            atributo_especifico = input(
                f"Endereço IP [{ativo.endereco_ip}]: "
            ).strip()


        elif isinstance(ativo, AplicacaoWeb):

            atributo_especifico = input(
                f"URL [{ativo.url}]: "
            ).strip()


        # ENTER mantém os valores atuais

        if nome == "":
            nome = None

        if setor == "":
            setor = None

        if atributo_especifico == "":
            atributo_especifico = None


        atualizado = self.inventario.atualizar_ativo(
            id_ativo,
            nome,
            responsavel,
            setor,
            atributo_especifico
        )


        if not atualizado:

            print(
                "Não foi possível atualizar o ativo."
            )

            return


        # Salva todas as alterações no final
        self.persistencia.salvar(
            self.inventario.listar_ativos()
        )


        print(
            "Atualização concluída com sucesso!"
        )

    
    def atualizar_vulnerabilidade_do_ativo(
        self,
        ativo
    ):
        if not ativo.vulnerabilidades:
            print("Este ativo não possui vulnerabilidades.")

            return
        
        print(
            "\n--- VULNERABILIDADES DO ATIVO ---"
        )

        for vulnerabilidade in ativo.vulnerabilidades:
            vulnerabilidade.exibir_vulnerabilidade()
            print("-" * 40)
        
        try:
            id_vulnerabilidade = int(input(
                "Digite o ID da vulnerabilidade"
                "que deseja atualizar"
                )
            )
        
        except ValueError:

            print(
                "O ID deve ser um número inteiro."
            )

            return


        vulnerabilidade = (
            self.inventario.buscar_vulnerabilidade_no_ativo(
                ativo.id,
                id_vulnerabilidade
            )
        )


        if vulnerabilidade is None:

            print(
                "Vulnerabilidade não encontrada neste ativo."
            )

            return


        print(
            "\nPressione ENTER para manter o valor atual."
        )


        descricao = input(
            f"Descrição [{vulnerabilidade.descricao}]: "
        ).strip()


        categoria = input(
            f"Categoria [{vulnerabilidade.categoria}]: "
        ).strip()


        severidade = input(
            f"Severidade [{vulnerabilidade.severidade}]: "
        ).strip()


        print("\nStatus disponíveis:")

        for tratamento in Tratamento:

            print(
                f"{tratamento.value} - "
                f"{tratamento.name}"
            )


        codigo_status = input(
            "Novo status "
            "(ENTER mantém o atual): "
        ).strip()
 
        # ENTER MANTÉM O VALOR ATUAL
      
        if descricao == "":
            descricao = None

        if categoria == "":
            categoria = None


        if severidade == "":

            severidade = None

        else:

            try:
                severidade = float(
                    severidade
                )

            except ValueError:

                print(
                    "A severidade deve ser numérica."
                )

                return


        status = None


        if codigo_status != "":

            try:

                status = Tratamento(
                    int(codigo_status)
                )

            except ValueError:

                print(
                    "Status inválido."
                )

                return


        try:

            atualizado = (
                self.inventario.atualizar_vulnerabilidade(
                    ativo.id,
                    id_vulnerabilidade,
                    descricao,
                    categoria,
                    severidade,
                    status
                )
            )

        except ValueError as erro:

            print(erro)

            return


        if atualizado:

            print(
                "Vulnerabilidade atualizada com sucesso!"
            )

        else:

            print(
                "Não foi possível atualizar "
                "a vulnerabilidade."
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