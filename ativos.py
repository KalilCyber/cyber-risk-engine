from abc import ABC, abstractmethod
from enums import NivelDependencia


# ============================================================
# CLASSE BASE DOS ATIVOS
# ============================================================

class Ativo(ABC):

    def __init__(
        self,
        id,
        nome,
        responsavel,
        setor,
        tipo,
        vulnerabilidades=None
    ):
        self.id = id
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.tipo = tipo

        if vulnerabilidades is None:
            self.vulnerabilidades = []
        else:
            self.vulnerabilidades = vulnerabilidades

        self.dependencias = []


    # --------------------------------------------------------
    # Adicionar vulnerabilidade
    # --------------------------------------------------------

    def adicionar_vulnerabilidade(self, vulnerabilidade):

        self.vulnerabilidades.append(
            vulnerabilidade
        )


    # --------------------------------------------------------
    # Exibir atributos comuns
    # --------------------------------------------------------

    @abstractmethod
    def exibir_ativo(self):

        print(f"ID: {self.id}")
        print(f"Nome: {self.nome}")
        print(f"Responsável: {self.responsavel}")
        print(f"Setor: {self.setor}")
        print(f"Tipo: {self.tipo}")

        print(
            "Quantidade de vulnerabilidades: "
            f"{len(self.vulnerabilidades)}"
        )


        print("Vulnerabilidades:")

        if not self.vulnerabilidades:

            print("Nenhuma vulnerabilidade cadastrada.")

        else:

            for vulnerabilidade in self.vulnerabilidades:

                print(
                    f"- {vulnerabilidade}"
                )


    def adicionar_dependencia(
        self,
        id_ativo_origem,
        nivel
    ):

        if not isinstance(
            nivel,
            NivelDependencia
        ):

            raise ValueError(
                "Nível de dependência inválido."
            )


        if id_ativo_origem == self.id:

            raise ValueError(
                "Um ativo não pode depender de si mesmo."
            )


        # ========================================================
        # CONVERSÃO DA ESCALA PARA O PESO DA MATRIZ A
        # ========================================================

        valor_nist = nivel.value

        peso = (
            valor_nist / 20
        )


        # ========================================================
        # VERIFICA DUPLICIDADE
        # ========================================================

        for dependencia in self.dependencias:

            if (
                dependencia["id_ativo_origem"]
                == id_ativo_origem
            ):

                raise ValueError(
                    "A dependência já foi adicionada."
                )


        # ========================================================
        # VERIFICA SOMA DOS PESOS
        # ========================================================

        soma_atual = sum(
            dependencia["peso"]
            for dependencia in self.dependencias
        )


        if soma_atual + peso >= 1:

            raise ValueError(
                "A soma dos pesos das dependências "
                "deve permanecer menor que 1."
            )


        # ========================================================
        # ARMAZENA A DEPENDÊNCIA
        # ========================================================

        self.dependencias.append(
            {
                "id_ativo_origem": id_ativo_origem,
                "nivel": nivel.name,
                "valor_nist": valor_nist,
                "peso": peso
            }
        )
        
# NOTEBOOK

class Notebook(Ativo):

    def __init__(
        self,
        id,
        nome,
        responsavel,
        setor,
        vulnerabilidades,
        processador
    ):
        super().__init__(
            id,
            nome,
            responsavel,
            setor,
            "Notebook",
            vulnerabilidades
        )

        self.processador = processador
       




    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Processador: {self.processador}"
        )


# SERVIDOR

class Servidor(Ativo):

    def __init__(
        self,
        id,
        nome,
        responsavel,
        setor,
        vulnerabilidades,
        servico
    ):
        super().__init__(
            id,
            nome,
            responsavel,
            setor,
            "Servidor",
            vulnerabilidades
        )

        self.servico = servico


    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Serviço: {self.servico}"
        )


# ROTEADOR

class Roteador(Ativo):

    def __init__(
        self,
        id,
        nome,
        responsavel,
        setor,
        vulnerabilidades,
        endereco_ip
    ):
        super().__init__(
            id,
            nome,
            responsavel,
            setor,
            "Roteador",
            vulnerabilidades
        )

        self.endereco_ip = endereco_ip


    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Endereço IP: {self.endereco_ip}"
        )

## APLICAÇÃO WEB

class AplicacaoWeb(Ativo):

    def __init__(
        self,
        id,
        nome,
        responsavel,
        setor,
        vulnerabilidades,
        url
        ):
       
        super().__init__(
            id,
            nome,
            responsavel,
            setor,
            "AplicacaoWeb",
            vulnerabilidades
        )

        self.url = url


    def exibir_ativo(self):

        super().exibir_ativo()
        print(f"URL: {self.url}")
