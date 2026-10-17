import numpy as np


class ModeloRisco:

    def __init__(
        self,
        inventario
    ):

        self.inventario = inventario

        self.ativos = []
        self.vulnerabilidades = []

        self.matriz_m = None
        self.vetor_v = None
        self.vetor_b = None


    def obter_vulnerabilidades_unicas(self):

        catalogo = {}

        for ativo in self.inventario.listar_ativos():

            for vulnerabilidade in ativo.vulnerabilidades:

                chave = (
                    vulnerabilidade
                    .obter_chave_modelo()
                )

                if chave not in catalogo:

                    catalogo[chave] = vulnerabilidade


        self.vulnerabilidades = list(
            catalogo.values()
        )

        return self.vulnerabilidades


    def obter_ativos(self):

        self.ativos = (
            self.inventario.listar_ativos()
        )

        return self.ativos


    def construir_matriz_m(self):

        self.obter_ativos()

        self.obter_vulnerabilidades_unicas()


        quantidade_ativos = len(
            self.ativos
        )

        quantidade_vulnerabilidades = len(
            self.vulnerabilidades
        )


        self.matriz_m = np.zeros(
            (
                quantidade_ativos,
                quantidade_vulnerabilidades
            ),
            dtype=int
        )


        for i, ativo in enumerate(
            self.ativos
        ):

            for vulnerabilidade in ativo.vulnerabilidades:

                chave = (
                    vulnerabilidade
                    .obter_chave_modelo()
                )


                for j, vulnerabilidade_modelo in enumerate(
                    self.vulnerabilidades
                ):

                    if (
                        chave
                        == vulnerabilidade_modelo.obter_chave_modelo()
                    ):

                        self.matriz_m[
                            i,
                            j
                        ] = 1


        return self.matriz_m


    def construir_vetor_v(self):

        if not self.vulnerabilidades:

            self.obter_vulnerabilidades_unicas()


        severidades = []


        for vulnerabilidade in self.vulnerabilidades:

            severidades.append(
                vulnerabilidade.severidade
            )


        self.vetor_v = np.array(
            severidades,
            dtype=float
        )


        return self.vetor_v


    def calcular_risco_proprio(self):

        self.construir_matriz_m()

        self.construir_vetor_v()


        self.vetor_b = (
            self.matriz_m
            @ self.vetor_v
        )


        return self.vetor_b