class Vulnerabilidade:

    def __init__(
        self,
        id,
        descricao,
        categoria,
        severidade,
        status
    ):
        self.id = id
        self.descricao = descricao
        self.categoria = categoria

        # A severidade será numérica porque futuramente
        # será utilizada no cálculo de risco.
        self.severidade = float(severidade)

        if self.severidade < 0 or self.severidade > 10:
            raise ValueError(
                "A severidade deve estar entre 0 e 10."
            )

        self.status = status


    def exibir_vulnerabilidade(self):

        print(f"ID da vulnerabilidade: {self.id}")
        print(f"Descrição: {self.descricao}")
        print(f"Categoria: {self.categoria}")
        print(f"Severidade: {self.severidade}")
        print(f"Status: {self.status}")


    def para_dict(self):

        return {
            "id": self.id,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "severidade": self.severidade,
            "status": self.status
        }


    @classmethod
    def de_dict(cls, dados):

        return cls(
            dados["id"],
            dados["descricao"],
            dados["categoria"],
            dados["severidade"],
            dados["status"]
        )


    def __str__(self):

        return (
            f"{self.descricao} | "
            f"Categoria: {self.categoria} | "
            f"Severidade: {self.severidade} | "
            f"Status: {self.status}"
        )