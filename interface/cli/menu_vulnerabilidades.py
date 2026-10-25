from dominio.vulnerabilidades import Vulnerabilidade
from dominio.enums import Tratamento

from interface.cli.menu_base import MenuBase


class MenuVulnerabilidades(MenuBase):

    def __init__(
        self,
        inventario,
        persistencia,
        servico_cve
    ):

        super().__init__(
            inventario,
            persistencia
        )

        self.servico_cve = servico_cve


    def executar(self):

        while True:

            print(
                "\n===== GERENCIAR VULNERABILIDADES ====="
            )

            print(
                "1 - Cadastrar vulnerabilidade"
            )

            print(
                "2 - Listar vulnerabilidades de um ativo"
            )

            print(
                "3 - Atualizar vulnerabilidade"
            )

            print(
                "0 - Voltar"
            )


            opcao = input(
                "Escolha uma opção: "
            ).strip()


            if opcao == "1":

                self.cadastrar_vulnerabilidade()


            elif opcao == "2":

                self.listar_vulnerabilidades()


            elif opcao == "3":

                self.atualizar_vulnerabilidade_menu()


            elif opcao == "0":

                break


            else:

                print(
                    "Opção inválida."
                )

    def cadastrar_vulnerabilidade(self):

        print(
            "\n--- CADASTRAR VULNERABILIDADE ---"
        )


        # ========================================================
        # ID DO ATIVO
        # ========================================================

        try:

            id_ativo = int(
                input(
                    "ID do ativo: "
                )
            )

        except ValueError:

            print(
                "O ID do ativo deve ser um número inteiro."
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


        # ========================================================
        # ID INTERNO DA VULNERABILIDADE
        # ========================================================

        try:

            id_vulnerabilidade = int(
                input(
                    "ID interno da vulnerabilidade: "
                )
            )

        except ValueError:

            print(
                "O ID da vulnerabilidade "
                "deve ser um número inteiro."
            )

            return


        # ========================================================
        # FORMA DE CADASTRO
        # ========================================================

        print(
            "\nComo deseja cadastrar a vulnerabilidade?"
        )

        print(
            "1 - Pesquisar pelo nome na NVD"
        )

        print(
            "2 - Cadastro manual"
        )


        opcao = input(
            "Escolha uma opção: "
        ).strip()


        # Esses campos serão usados quando
        # a vulnerabilidade vier da NVD.
        cve_id = None
        cwe_id = None
        cvss_vector = None
        cvss_version = None


        # ========================================================
        # OPÇÃO 1 - PESQUISA NA NVD
        # ========================================================

        if opcao == "1":

            termo = self.ler_campo_obrigatorio(
                "Nome da vulnerabilidade: "
            )


            print(
                "\nConsultando a NVD..."
            )


            try:

                resultados = (
                    self.servico_cve.pesquisar_por_nome(
                        termo
                    )
                )

            except ConnectionError as erro:

                print(
                    f"Erro ao consultar a NVD: {erro}"
                )

                return


            if not resultados:

                print(
                    "Nenhuma vulnerabilidade encontrada."
                )

                return


            # ====================================================
            # MOSTRA OS CVEs ENCONTRADOS
            # ====================================================

            print(
                "\n--- RESULTADOS ENCONTRADOS ---"
            )


            for indice, resultado in enumerate(
                resultados,
                start=1
            ):

                cvss = resultado["cvss"]

                descricao_resumida = self.resumir_texto(
                    resultado["descricao"]
                )


                print(
                    "\n----------------------------"
                )

                print(
                    f"{indice} - "
                    f"{resultado['cve_id']}"
                )

                print(
                    f"CWE: "
                    f"{resultado['cwe_id'] or 'Não informado'}"
                )

                print(
                    f"CVSS: "
                    f"{cvss['score']}"
                )

                print(
                    f"Versão CVSS: "
                    f"{cvss['versao']}"
                )

                print(
                    f"Descrição: "
                    f"{resultado['descricao']}"
                )



            # USUÁRIO ESCOLHE UM CVE

            entrada = input(
                "\nEscolha pelo número ou digite o CVE: "
            ).strip().upper()

            # ESCOLHA PELO NÚMERO
            
            if entrada.isdigit():

                escolha = int(
                    entrada
                )


                if (
                    escolha < 1
                    or escolha > len(resultados)
                ):

                    print(
                        "Escolha inválida."
                    )

                    return


                selecionado = resultados[
                    escolha - 1
                ]


            # ====================================================
            # ESCOLHA PELO CVE
            # ====================================================

            else:

                selecionado = None


                for resultado in resultados:

                    if (
                        resultado["cve_id"].upper()
                        == entrada
                    ):

                        selecionado = resultado

                        break


                if selecionado is None:

                    print(
                        "CVE não encontrado entre "
                        "os resultados apresentados."
                    )

                    return


            # ====================================================
            # CVE SELECIONADO
            # ====================================================

            cvss = selecionado[
                "cvss"
            ]

            

            cvss = selecionado[
                "cvss"
            ]


            # ====================================================
            # DADOS PREENCHIDOS AUTOMATICAMENTE
            # ====================================================

            descricao = selecionado[
                "descricao"
            ]

            cve_id = selecionado[
                "cve_id"
            ]

            cwe_id = selecionado[
                "cwe_id"
            ]

            severidade = cvss[
                "score"
            ]

            cvss_vector = cvss[
                "vetor"
            ]

            cvss_version = cvss[
                "versao"
            ]


            # Usamos o CWE como categoria quando disponível.
            if cwe_id:

                categoria = cwe_id

            else:

                categoria = termo


            print(
                "\n--- VULNERABILIDADE SELECIONADA ---"
            )

            print(
                f"CVE: {cve_id}"
            )

            print(
                f"CWE: {cwe_id or 'Não informado'}"
            )

            print(
                f"CVSS: {severidade}"
            )

            print(
                f"Versão CVSS: {cvss_version}"
            )

            print(
                f"Vetor CVSS: {cvss_vector}"
            )


        # ========================================================
        # OPÇÃO 2 - CADASTRO MANUAL
        # ========================================================

        elif opcao == "2":

            descricao = self.ler_campo_obrigatorio(
                "Descrição: "
            )


            categoria = self.ler_campo_obrigatorio(
                "Categoria: "
            )


            try:

                severidade = float(
                    input(
                        "Severidade (0 a 10): "
                    )
                )

            except ValueError:

                print(
                    "A severidade deve ser um número."
                )

                return


        else:

            print(
                "Opção inválida."
            )

            return


        # ========================================================
        # STATUS
        # ========================================================

        print(
            "\nStatus disponíveis:"
        )


        for tratamento in Tratamento:

            print(
                f"{tratamento.value} - "
                f"{tratamento.name}"
            )


        try:

            codigo_status = int(
                input(
                    "Escolha o status: "
                )
            )

            status = Tratamento(
                codigo_status
            )

        except ValueError:

            print(
                "Status inválido."
            )

            return


        # ========================================================
        # CRIA O OBJETO VULNERABILIDADE
        # ========================================================

        try:

            vulnerabilidade = Vulnerabilidade(
                id_vulnerabilidade,
                descricao,
                categoria,
                severidade,
                status,
                cve_id,
                cwe_id,
                cvss_vector,
                cvss_version,
            )

        except ValueError as erro:

            print(
                erro
            )

            return


        # ========================================================
        # ASSOCIA AO ATIVO
        # ========================================================

        try:

            adicionada = (
                self.inventario.associar_vulnerabilidade(
                    id_ativo,
                    vulnerabilidade
                )
            )

        except ValueError as erro:

            print(
                erro
            )

            return


        if not adicionada:

            print(
                "Não foi possível adicionar "
                "a vulnerabilidade."
            )

            return


        # ========================================================
        # SALVA NO JSON
        # ========================================================

        self.persistencia.salvar(
            self.inventario.listar_ativos()
        )


        print(
            "\nVulnerabilidade cadastrada com sucesso!"
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

    
    def atualizar_vulnerabilidade_menu(self):

        print(
            "\n--- ATUALIZAR VULNERABILIDADE ---"
        )


        try:

            id_ativo = int(
                input(
                    "ID do ativo: "
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


        atualizado = (
            self.atualizar_vulnerabilidade_do_ativo(
                 ativo
             )
        )

        if atualizado:
            self.salvar_dados()
        

    
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
                " que deseja atualizar: "
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

        descricao_resumida = self.resumir_texto(
            vulnerabilidade.descricao
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

            return True


        print(
            "Não foi possível atualizar "
        "a vulnerabilidade."
            )

        return False    