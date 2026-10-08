from abc import ABC, abstractmethod


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
        vulnerabilidades=None
    ):
        self.id = id
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor

        if vulnerabilidades is None:
            self.vulnerabilidades = []
        else:
            self.vulnerabilidades = vulnerabilidades


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


        print("Vulnerabilidades:")

        if not self.vulnerabilidades:

            print("Nenhuma vulnerabilidade cadastrada.")

        else:

            for vulnerabilidade in self.vulnerabilidades:

                print(
                    f"- {vulnerabilidade}"
                )


# ============================================================
# NOTEBOOK
# ============================================================

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
            vulnerabilidades
        )

        self.processador = processador


    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Processador: {self.processador}"
        )


# ============================================================
# SERVIDOR
# ============================================================

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
            vulnerabilidades
        )

        self.servico = servico


    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Serviço: {self.servico}"
        )


# ============================================================
# ROTEADOR
# ============================================================

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
            vulnerabilidades
        )

        self.endereco_ip = endereco_ip


    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Endereço IP: {self.endereco_ip}"
        )