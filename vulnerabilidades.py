from enums import Tratamento


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

        # Severidade numérica para o cálculo de risco
        self.severidade = float(severidade)

        if not 0 <= self.severidade <= 10:
            raise ValueError(
                "A severidade deve estar entre 0 e 10."
            )

        # Garante que o status seja um Enum Tratamento
        if not isinstance(status, Tratamento):
            raise ValueError(
                "Status inválido. Use o Enum Tratamento."
            )

        self.status = status


    # Exibição da vulnerabilidade
    def exibir_vulnerabilidade(self):

        print(f"ID da vulnerabilidade: {self.id}")
        print(f"Descrição: {self.descricao}")
        print(f"Categoria: {self.categoria}")
        print(f"Severidade: {self.severidade}")
        print(f"Status: {self.status.name}")


    # Converte o objeto para dicionário
    def para_dict(self):

        return {
            "id": self.id,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "severidade": self.severidade,
            "status": self.status.name
        }


    # Reconstrói o objeto a partir de um dicionário
    @classmethod
    def de_dict(cls, dados):

        try:
            status = Tratamento[dados["status"]]

        except (KeyError, TypeError) as erro:
            raise ValueError(
                f"Status inválido no JSON: {dados['status']}"
            ) from erro

        return cls(
            dados["id"],
            dados["descricao"],
            dados["categoria"],
            dados["severidade"],
            status
        )


    # Representação textual do objeto
    def __str__(self):

        return (
            f"{self.descricao} | "
            f"Categoria: {self.categoria} | "
            f"Severidade: {self.severidade} | "
            f"Status: {self.status.name}"
        )