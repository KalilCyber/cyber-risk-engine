from dominio.enums import Tratamento


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


        # SEVERIDADE

        self.severidade = float(
            severidade
        )


        if not 0 <= self.severidade <= 10:

            raise ValueError(
                "A severidade deve estar entre 0 e 10."
            )


        # STATUS

        if isinstance(
            status,
            Tratamento
        ):

            self.status = status


        elif isinstance(
            status,
            str
        ):

            # Compatibilidade com dados antigos
            if status == "ABERTA":
                status = "ABERTO"


            try:

                self.status = Tratamento[
                    status
                ]

            except KeyError:

                raise ValueError(
                    "Status inválido. "
                    "Use o Enum Tratamento."
                )


        else:

            raise ValueError(
                "Status inválido. "
                "Use o Enum Tratamento."
            )


    # EXIBIR VULNERABILIDADE

    def exibir_vulnerabilidade(self):

        limite_descricao = 50

        if len(self.descricao) > limite_descricao:

            descricao_resumida = (
                self.descricao[
                    :limite_descricao - 3
                ].rstrip()
                + "..."
            )

        else:

            descricao_resumida = (
                self.descricao
            )


        print(
            f"ID interno: {self.id}"
        )


        if self.cve_id:

            print(
                f"CVE: {self.cve_id}"
            )


        if self.cwe_id:

            print(
                f"CWE: {self.cwe_id}"
            )


        print(
            f"Descrição: {descricao_resumida}"
        )


        print(
            f"Categoria: {self.categoria}"
        )


        print(
            f"Severidade CVSS: {self.severidade}"
        )

        print(
            f"Severidade considerada: "
            f"{self.obter_severidade_efetiva()}"
        )


        if self.cvss_version:

            print(
                f"Versão CVSS: {self.cvss_version}"
            )


        if self.cvss_vector:

            print(
                f"Vetor CVSS: {self.cvss_vector}"
            )


        print(
            f"Status: {self.status.name}"
        )

    # ATUALIZAR VULNERABILIDADE

    def atualizar(
        self,
        descricao=None,
        categoria=None,
        severidade=None,
        status=None
    ):

        if descricao is not None:
            self.descricao = descricao


        if categoria is not None:
            self.categoria = categoria


        if severidade is not None:

            severidade = float(
                severidade
            )


            if severidade < 0 or severidade > 10:

                raise ValueError(
                    "A severidade deve estar entre 0 e 10."
                )


            self.severidade = severidade


        if status is not None:

            if isinstance(
                status,
                Tratamento
            ):

                self.status = status

            else:

                raise ValueError(
                    "Status inválido. "
                    "Use o Enum Tratamento."
                )

    def obter_severidade_efetiva(self):

        if self.status == Tratamento.CORRIGIDA:
            return 0.0

        return self.severidade


    # CHAVE PARA O MODELO DE RISCO

    def obter_chave_modelo(self):

        if self.cve_id:

            return self.cve_id


        return f"MANUAL-{self.id}"


    # CONVERTER OBJETO PARA DICIONÁRIO

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


    # RECONSTRUIR OBJETO A PARTIR DO JSON
  

    @classmethod
    def de_dict(
        cls,
        dados
    ):

        try:

            status_texto = dados[
                "status"
            ]


            # Compatibilidade com registros antigos
            if status_texto == "ABERTA":
                status_texto = "ABERTO"


            status = Tratamento[
                status_texto
            ]


        except (
            KeyError,
            TypeError
        ) as erro:

            raise ValueError(
                f"Status inválido no JSON: "
                f"{dados.get('status')}"
            ) from erro


        return cls(
            dados["id"],
            dados["descricao"],
            dados["categoria"],
            dados["severidade"],
            status,
            dados.get("cve_id"),
            dados.get("cwe_id"),
            dados.get("cvss_vector"),
            dados.get("cvss_version")
        )


    # REPRESENTAÇÃO TEXTUAL

    def __str__(self):

        limite_descricao = 50

        if len(self.descricao) > limite_descricao:

            descricao_resumida = (
                self.descricao[:limite_descricao - 3].rstrip()
                + "..."
            )

        else:

            descricao_resumida = self.descricao


        return (
            f"{descricao_resumida} | "
            f"Categoria: {self.categoria} | "
            f"Severidade: {self.severidade} | "
            f"Status: {self.status.name}"
        )

    # COMPARAÇÃO DE VULNERABILIDADES

    def possui_mesmos_dados(
        self,
        outra
    ):

        return (
            self.id == outra.id
            and self.descricao == outra.descricao
            and self.categoria == outra.categoria
            and self.severidade == outra.severidade
        )
    
    def to_dict(self):
        return self.para_dict()
    
    @classmethod
    def from_dict(cls, dados):
        return cls.de_dict(dados)