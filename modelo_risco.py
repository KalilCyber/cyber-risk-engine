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
        self.matriz_a = None
        self.matriz_sistema = None
        self.vetor_x = None
        self.numero_condicao = None


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

    def construir_matriz_a(self):

        if not self.ativos:
            self.obter_ativos()


        quantidade_ativos = len(
            self.ativos
        )


        self.matriz_a = np.zeros(
            (
                quantidade_ativos,
                quantidade_ativos
            ),
            dtype=float
        )


        # Relaciona o ID de cada ativo
        # com sua posição na matriz
        indices_ativos = {}

        for indice, ativo in enumerate(
            self.ativos
        ):

            indices_ativos[
                ativo.id
            ] = indice


        # Percorre cada ativo que recebe risco
        for i, ativo_destino in enumerate(
            self.ativos
        ):

            for dependencia in (
                ativo_destino.dependencias
            ):

                id_origem = dependencia[
                    "id_ativo_origem"
                ]

                peso = dependencia[
                    "peso"
                ]


                if id_origem not in indices_ativos:

                    raise ValueError(
                        f"O ativo de origem ID "
                        f"{id_origem} não existe "
                        "no inventário."
                    )


                j = indices_ativos[
                    id_origem
                ]


                self.matriz_a[
                    i,
                    j
                ] = peso


        return self.matriz_a

    def construir_matriz_sistema(self):

        self.construir_matriz_a()


        quantidade_ativos = len(
            self.ativos
        )


        matriz_identidade = np.eye(
            quantidade_ativos,
            dtype=float
        )


        self.matriz_sistema = (
            matriz_identidade
            - self.matriz_a
        )


        return self.matriz_sistema


    def calcular_risco_efetivo(self):

        self.calcular_risco_proprio()

        self.construir_matriz_sistema()


        quantidade_ativos = len(
            self.ativos
        )


        if quantidade_ativos == 0:

            self.vetor_x = np.array(
                [],
                dtype=float
            )

            return self.vetor_x


        posto = np.linalg.matrix_rank(
            self.matriz_sistema
        )


        if posto < quantidade_ativos:

            raise ValueError(
                "A matriz (I - A) não é invertível. "
                "Não é possível calcular o risco efetivo."
            )


        self.numero_condicao = np.linalg.cond(
            self.matriz_sistema
        )


        try:

            self.vetor_x = np.linalg.solve(
                self.matriz_sistema,
                self.vetor_b
            )


        except np.linalg.LinAlgError as erro:

            raise ValueError(
                "Não foi possível resolver "
                "o sistema de risco."
            ) from erro


        return self.vetor_x