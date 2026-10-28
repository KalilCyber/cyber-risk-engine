from dominio.ativos import (
    Notebook,
    Servidor,
    Roteador,
    AplicacaoWeb
)

from interface.cli.menu_base import MenuBase



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


            opcao = self.ler_opcao('Escolha uma opção: ', ('0', '1', '2', '3', '4', '5'))


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

            id_ativo = self.ler_inteiro_positivo('ID do ativo: ')

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


        tipo = self.ler_opcao('Escolha o tipo: ', ("1", "2", "3", "4"))


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

            endereco_ip = self.ler_texto("Endereço IP: ", tipo="ip")

            ativo = Roteador(
                id_ativo,
                nome,
                responsavel,
                setor,
                [],
                endereco_ip
            )


        elif tipo == "4":

            url = self.ler_texto("URL: ", tipo="url")

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


        self.salvar_dados()


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


        opcao = self.ler_opcao('Escolha uma opção: ', ('1', '2'))


        # ----------------------------------------------------
        # BUSCA POR ID
        # ----------------------------------------------------

        if opcao == "1":

            try:

                id_ativo = self.ler_inteiro_positivo('Digite o ID: ')

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

            nome = self.ler_texto('Digite o nome ou parte do nome: ', permitir_vazio=False)


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

            id_ativo = self.ler_inteiro_positivo('Digite o ID do ativo: ')

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
  
        nome = self.ler_texto(f'Nome [{ativo.nome}]: ', permitir_vazio=True)


        responsavel = self.ler_responsavel(
            f"Responsável [{ativo.responsavel}]: ",
            permitir_vazio=True
        )


        setor = self.ler_texto(f'Setor [{ativo.setor}]: ', permitir_vazio=True)


        
        # ATRIBUTO ESPECÍFICO

        atributo_especifico = None


        if isinstance(ativo, Notebook):

            atributo_especifico = self.ler_texto(f'Processador [{ativo.processador}]: ', permitir_vazio=True, tipo='texto')


        elif isinstance(ativo, Servidor):

            atributo_especifico = self.ler_texto(f'Serviço [{ativo.servico}]: ', permitir_vazio=True, tipo='texto')


        elif isinstance(ativo, Roteador):

            atributo_especifico = self.ler_texto(f'Endereço IP [{ativo.endereco_ip}]: ', permitir_vazio=True, tipo='ip')


        elif isinstance(ativo, AplicacaoWeb):

            atributo_especifico = self.ler_texto(f'URL [{ativo.url}]: ', permitir_vazio=True, tipo='url')


        # ENTER mantém os valores atuais

        if nome == "":
            nome = None

        if setor == "":
            setor = None

        if atributo_especifico == "":
            atributo_especifico = None

        try:
            atualizado = self.inventario.atualizar_ativo(
                id_ativo,
                nome,
                responsavel,
                setor,
                atributo_especifico
            )

        except ValueError as erro:
            print(f"Erro na atualização: {erro}")
            return


        # Salva todas as alterações no final
        self.salvar_dados()


        print(
            "Atualização concluída com sucesso!"
        )

    

    
    # REMOVER ATIVO

    def remover_ativo(self):

        print(
            "\n--- REMOVER ATIVO ---"
        )


        try:

            id_ativo = self.ler_inteiro_positivo('Digite o ID do ativo: ')

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


        confirmacao = self.ler_opcao('\nDeseja realmente remover este ativo? (s/n): ', ("s", "n"))


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

            self.salvar_dados()

            print(
                "Ativo removido com sucesso!"
            )

        else:

            print(
                "Não foi possível remover o ativo."
            )