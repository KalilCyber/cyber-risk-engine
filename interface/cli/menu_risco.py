from dominio.enums import Tratamento, NivelDependencia
from servicos.modelo_risco import ModeloRisco

from interface.cli.menu_base import MenuBase


class MenuRisco(MenuBase):

    def executar(self):

        while True:

            print(
                "\n===== ANÁLISE DE RISCO ====="
            )

            print(
                "1 - Cadastrar dependência entre ativos"
            )

            print(
                "2 - Listar dependências de um ativo"
            )

            print(
                "3 - Calcular risco dos ativos"
            )

            print(
                "4 - Exibir matrizes do modelo"
            )

            print(
                "0 - Voltar"
            )


            opcao = input(
                "Escolha uma opção: "
            ).strip()


            if opcao == "1":

                self.cadastrar_dependencia()


            elif opcao == "2":

                self.listar_dependencias()


            elif opcao == "3":

                self.calcular_risco()


            elif opcao == "4":

                self.exibir_matrizes()


            elif opcao == "0":

                break


            else:

                print(
                    "Opção inválida."
                )

    
    def cadastrar_dependencia(self):

        print(
            "\n--- CADASTRAR DEPENDÊNCIA ENTRE ATIVOS ---"
        )


        try:

            id_destino = int(
                input(
                    "ID do ativo que recebe o risco: "
                )
            )


            id_origem = int(
                input(
                    "ID do ativo que transmite o risco: "
                )
            )


            print(
                "\nNíveis de dependência:"
            )


            niveis = list(
                NivelDependencia
            )


            for indice, nivel in enumerate(
                niveis,
                start=1
            ):

                peso = (
                    nivel.value / 20
                )


                print(
                    f"{indice} - "
                    f"{nivel.name} "
                    f"| Valor de referência: {nivel.value} "
                    f"| Peso: {peso:.2f}"
                )


            codigo = int(
                input(
                    "Escolha o nível da dependência: "
                )
            )


            if (
                codigo < 1
                or codigo > len(niveis)
            ):

                raise ValueError(
                    "Nível de dependência inválido."
                )


            nivel_selecionado = (
                niveis[
                    codigo - 1
                ]
            )


            self.inventario.cadastrar_dependencia(
                id_destino,
                id_origem,
                nivel_selecionado
            )


            self.salvar_dados()


            peso = (
                nivel_selecionado.value
                / 20
            )


            print(
                "\nDependência cadastrada com sucesso!"
            )

            print(
                f"Nível: "
                f"{nivel_selecionado.name}"
            )

            print(
                f"Valor de referência: "
                f"{nivel_selecionado.value}"
            )

            print(
                f"Peso utilizado em A: "
                f"{peso:.2f}"
            )


        except ValueError as erro:

            print(
                f"Erro: {erro}"
            )
    

    def listar_dependencias(self):

        print(
            "\n--- DEPENDÊNCIAS DO ATIVO ---"
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


        if not ativo.dependencias:

            print(
                "Este ativo não possui "
                "dependências cadastradas."
            )

            return


        print(
            f"\nDependências de {ativo.nome}:"
        )


        for dependencia in ativo.dependencias:

            ativo_origem = (
                self.inventario.buscar_por_id(
                    dependencia[
                        "id_ativo_origem"
                    ]
                )
            )


            if ativo_origem is not None:

                nome_origem = (
                    ativo_origem.nome
                )

            else:

                nome_origem = (
                    "Ativo não encontrado"
                )


            nivel = dependencia.get(
                "nivel"
            )

            valor_nist = dependencia.get(
                "valor_nist"
            )


            if (
                nivel is not None
                and valor_nist is not None
            ):

                print(
                    f"- Recebe risco de "
                    f"{nome_origem} "
                    f"(ID {dependencia['id_ativo_origem']})"
                )

                print(
                    f"  Nível: {nivel}"
                )

                print(
                    f"  Valor de referência: "
                    f"{valor_nist}"
                )

                print(
                    f"  Peso em A: "
                    f"{dependencia['peso']:.2f}"
                )


            else:

                # Compatibilidade com dependências antigas
                print(
                    f"- Recebe "
                    f"{dependencia['peso'] * 100:.1f}% "
                    f"do risco de "
                    f"{nome_origem} "
                    f"(ID {dependencia['id_ativo_origem']})"
                )

    
    def calcular_risco(self):

        print(
            "\n===== RESULTADO DA ANÁLISE DE RISCO ====="
        )


        modelo = ModeloRisco(
            self.inventario
        )


        try:

            vetor_x = (
                modelo.calcular_risco_efetivo()
            )


        except ValueError as erro:

            print(
                f"Erro ao calcular risco: {erro}"
            )

            return


        if len(modelo.ativos) == 0:

            print(
                "Nenhum ativo cadastrado."
            )

            return


        for indice, ativo in enumerate(
            modelo.ativos
        ):

            risco_proprio = (
                modelo.vetor_b[
                    indice
                ]
            )

            risco_efetivo = (
                vetor_x[
                    indice
                ]
            )


            print(
                "\n----------------------------------------"
            )

            print(
                f"ID: {ativo.id}"
            )

            print(
                f"Ativo: {ativo.nome}"
            )

            print(
                f"Risco próprio: "
                f"{risco_proprio:.4f}"
            )

            print(
                f"Risco efetivo: "
                f"{risco_efetivo:.4f}"
            )


        print(
            "\n----------------------------------------"
        )

        print(
            f"Número de condição: "
            f"{modelo.numero_condicao:.4f}"
        )
    
    def exibir_matrizes(self):

        print(
            "\n===== MATRIZES DO MODELO DE RISCO ====="
        )

        modelo = ModeloRisco(
            self.inventario
        )

        try:
            modelo.calcular_risco_efetivo()

        except ValueError as erro:
            print(
                f"Erro ao construir o modelo: {erro}"
            )

            return
        
        print(
        "\n--- MATRIZ M ---"
    )

        print(
            modelo.matriz_m
        )


        print(
            "\n--- VETOR v ---"
        )

        print(
            modelo.vetor_v
        )


        print(
            "\n--- VETOR b = Mv ---"
        )

        print(
            modelo.vetor_b
        )


        print(
            "\n--- MATRIZ A ---"
        )

        print(
            modelo.matriz_a
        )


        print(
            "\n--- MATRIZ I - A ---"
        )

        print(
            modelo.matriz_sistema
        )


        print(
            "\n--- VETOR x ---"
        )

        print(
            modelo.vetor_x
        )


        print(
            "\n--- NÚMERO DE CONDIÇÃO ---"
        )

        print(
            modelo.numero_condicao
        )