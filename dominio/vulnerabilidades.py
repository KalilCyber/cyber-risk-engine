from dominio.enums import Tratamento


class Vulnerabilidade:

    @staticmethod
    def _validar_id(valor):
        if type(valor) is not int or valor <= 0:
            raise ValueError("O ID da vulnerabilidade deve ser um inteiro positivo.")
        return valor

    @staticmethod
    def _validar_texto(valor, campo):
        if not isinstance(valor, str):
            raise ValueError(f"{campo} deve ser um texto válido.")
        valor = valor.strip()
        if not valor or not any(caractere.isalpha() for caractere in valor):
            raise ValueError(f"{campo} deve conter pelo menos uma letra.")
        return valor

    @staticmethod
    def _validar_severidade(valor):
        if isinstance(valor, bool):
            raise ValueError("A severidade deve ser um número entre 0 e 10.")
        try:
            numero = float(valor)
        except (TypeError, ValueError) as erro:
            raise ValueError("A severidade deve ser um número entre 0 e 10.") from erro
        if not 0 <= numero <= 10:
            raise ValueError("A severidade deve estar entre 0 e 10.")
        return numero

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor):
        self._id = self._validar_id(valor)

    @property
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, valor):
        self._descricao = self._validar_texto(valor, "Descrição")

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, valor):
        self._categoria = self._validar_texto(valor, "Categoria")

    @property
    def severidade(self):
        return self._severidade

    @severidade.setter
    def severidade(self, valor):
        self._severidade = self._validar_severidade(valor)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, valor):
        if isinstance(valor, Tratamento):
            self._status = valor
            return
        if isinstance(valor, str):
            nome = "ABERTO" if valor == "ABERTA" else valor
            try:
                self._status = Tratamento[nome]
                return
            except KeyError:
                pass
        raise ValueError("Status inválido. Use o Enum Tratamento.")

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


        # A propriedade valida faixa numérica e rejeita NaN/infinito.
        self.severidade = severidade


        # O setter converte status antigo ABERTA e valida o Enum.
        self.status = status


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
        # Valida tudo ANTES de modificar qualquer atributo.
        nova_descricao = (
            self._validar_texto(descricao, "Descrição")
            if descricao is not None else None
        )
        nova_categoria = (
            self._validar_texto(categoria, "Categoria")
            if categoria is not None else None
        )
        nova_severidade = (
            self._validar_severidade(severidade)
            if severidade is not None else None
        )
        if status is not None and not isinstance(status, Tratamento):
            raise ValueError("Status inválido. Use o Enum Tratamento.")

        if nova_descricao is not None:
            self.descricao = nova_descricao
        if nova_categoria is not None:
            self.categoria = nova_categoria
        if nova_severidade is not None:
            self.severidade = nova_severidade
        if status is not None:
            self.status = status

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