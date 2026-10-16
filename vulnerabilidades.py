from enums import Tratamento


class Vulnerabilidade:

    def __init__(
        self,
        id,
        descricao,
        categoria,
        severidade,
        status,
        cve_id=None,
        cwe_id=None,
        cvss_vector=None,
        cvss_version=None    
    ):
        
        self.id = id
        self.descricao = descricao
        self.categoria = categoria
        self.cve_id = cve_id
        self.cwe_id = cwe_id
        self.cvss_vector = cvss_vector
        self.cvss_version = cvss_version


        # Severidade numérica para o cálculo de risco
        self.severidade = float(severidade)

        if not 0 <= self.severidade <= 10:
            raise ValueError(
                "A severidade deve estar entre 0 e 10."
            )

        if isinstance(status, Tratamento):

            self.status = status


        elif isinstance(status, str):

            # Compatibilidade com dados antigos
            if status == "ABERTA":
                status = "ABERTO"

            try:

                self.status = Tratamento[
                    status
                ]

            except KeyError:

                raise ValueError(
                    "Status inválido. Use o Enum Tratamento."
                )


        else:

            raise ValueError(
                "Status inválido. Use o Enum Tratamento."
            )


    # Exibição da vulnerabilidade
    def exibir_vulnerabilidade(self):

        print(f"ID da vulnerabilidade: {self.id}")
        print(f"Descrição: {self.descricao}")
        print(f"Categoria: {self.categoria}")
        print(f"Severidade: {self.severidade}")
        print(f"Status: {self.status.name}")

    
    def atualizar(self,
                  descricao=None,
                  categoria=None,
                  severidade=None,
                  status=None):
        
        if descricao is not None:
            self.descricao = descricao
        
        if categoria is not None:
            self.categoria = categoria
        
        if severidade is not None:
            severidade = float(severidade)
            if severidade < 0 or severidade > 10:
                raise ValueError(
                    "A severidade deveesar entre 0 e 10."
                )
            
            self.severidade = severidade
        
        if status is not None:
            self.status = status


    # Converte o objeto para dicionário
    def para_dict(self):

        return {
            "id": self.id,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "severidade": self.severidade,
            "status": self.status.name,
            "cve_id": self.cve_id,
            "cwe_id": self.cwe_id,
            "cvss_vector": self.cvss_vector,
            "cvss_version": self.cvss_version
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
            dados["status"],
            dados.get("cve_id"),
            dados.get("cwe_id"),
            dados.get("cvss_vector"),
            dados.get("cvss_version")
        )


    # Representação textual do objeto
    def __str__(self):

        return (
            f"{self.descricao} | "
            f"Categoria: {self.categoria} | "
            f"Severidade: {self.severidade} | "
            f"Status: {self.status.name}"
        )

    def possui_mesmos_dados(self, outra):

        return (
            self.id == outra.id
            and self.descricao == outra.descricao
            and self.categoria == outra.categoria
            and self.severidade == outra.severidade
            and self.status == outra.status
        )