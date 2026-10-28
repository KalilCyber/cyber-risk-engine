from abc import ABC, abstractmethod
from ipaddress import ip_address
from urllib.parse import urlsplit
import re
from dominio.enums import NivelDependencia


# ============================================================
# CLASSE BASE DOS ATIVOS
# ============================================================

class ValidacaoAtivo:
    """Regras compartilhadas pelos atributos e pelas entradas do menu."""

    @staticmethod
    def texto(valor, campo):
        if not isinstance(valor, str):
            raise ValueError(f"{campo} deve ser um texto.")
        valor = valor.strip()
        if not valor or not any(letra.isalpha() for letra in valor):
            raise ValueError(
                f"{campo} deve conter pelo menos uma letra; "
                "não use apenas números ou símbolos."
            )
        if any(not caractere.isprintable() for caractere in valor):
            raise ValueError(f"{campo} não pode conter caracteres de controle.")
        return valor

    @staticmethod
    def id_positivo(valor):
        # O domínio usa inteiros. O menu converte a entrada antes de chamar.
        if type(valor) is not int or valor <= 0:
            raise ValueError("O ID deve ser um número inteiro maior que zero.")
        return valor

    @staticmethod
    def endereco_ip(valor):
        if not isinstance(valor, str):
            raise ValueError("Informe um endereço IPv4 ou IPv6 válido.")
        valor = valor.strip()
        try:
            ip_address(valor)
        except ValueError as erro:
            raise ValueError(
                "Endereço IP inválido. Exemplo: 192.168.0.1."
            ) from erro
        return valor

    @staticmethod
    def url(valor):
        if not isinstance(valor, str):
            raise ValueError("Informe uma URL com http:// ou https://.")
        valor = valor.strip()
        mensagem = "URL inválida. Exemplo: https://sistema.exemplo.com."
        if not valor or any(
            caractere.isspace() or not caractere.isprintable()
            for caractere in valor
        ) or "\\" in valor:
            raise ValueError(mensagem)
        try:
            partes = urlsplit(valor)
            host = partes.hostname
            porta = partes.port
        except ValueError as erro:
            raise ValueError(mensagem) from erro
        if (
            partes.scheme not in ("http", "https")
            or not host
            or partes.username is not None
            or partes.password is not None
            or (porta is not None and porta < 1)
        ):
            raise ValueError(mensagem)
        try:
            ip_address(host)
        except ValueError:
            # Aceita localhost e nomes de rede interna, além de domínios.
            try:
                dominio = host.rstrip(".").encode("idna").decode("ascii")
            except UnicodeError as erro:
                raise ValueError(mensagem) from erro
            rotulos = dominio.split(".")
            if (
                len(dominio) > 253
                or all(c in "0123456789." for c in dominio)
                or any(
                    not re.fullmatch(
                        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?",
                        rotulo
                    )
                    for rotulo in rotulos
                )
            ):
                raise ValueError(mensagem)
        # Valida formato; não faz uma conexão com o endereço.
        return valor


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


    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._id = ValidacaoAtivo.id_positivo(valor)

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._nome = ValidacaoAtivo.texto(valor, "Nome")

    @property
    def responsavel(self):
        return self._responsavel

    @responsavel.setter
    def responsavel(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._responsavel = ValidacaoAtivo.texto(valor, "Responsável")

    @property
    def setor(self):
        return self._setor

    @setor.setter
    def setor(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._setor = ValidacaoAtivo.texto(valor, "Setor")

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._tipo = ValidacaoAtivo.texto(valor, "Tipo")

    # --------------------------------------------------------
    # Adicionar vulnerabilidade
    # --------------------------------------------------------

    def adicionar_vulnerabilidade(
        self,
        vulnerabilidade
    ):

        self.vulnerabilidades.append(
            vulnerabilidade
        )


    # --------------------------------------------------------
    # Converter ativo para dicionário
    # --------------------------------------------------------

    def to_dict(self):

        return {
            "id": self.id,
            "nome": self.nome,
            "responsavel": self.responsavel,
            "setor": self.setor,
            "tipo": self.tipo,

            "vulnerabilidades": [
                vulnerabilidade.to_dict()
                for vulnerabilidade
                in self.vulnerabilidades
            ],

            "dependencias": self.dependencias
        }


    # --------------------------------------------------------
    # Exibir atributos comuns
    # --------------------------------------------------------

    @abstractmethod
    def exibir_ativo(self):

        print(f"ID: {self.id}")
        print(f"Nome: {self.nome}")
        print(
            f"Responsável: {self.responsavel}"
        )
        print(f"Setor: {self.setor}")
        print(f"Tipo: {self.tipo}")

        print(
            "Quantidade de vulnerabilidades: "
            f"{len(self.vulnerabilidades)}"
        )

        print("Vulnerabilidades:")

        if not self.vulnerabilidades:

            print(
                "Nenhuma vulnerabilidade cadastrada."
            )

        else:

            for vulnerabilidade in (
                self.vulnerabilidades
            ):

                print(
                    f"- {vulnerabilidade}"
                )


    # --------------------------------------------------------
    # Adicionar dependência
    # --------------------------------------------------------

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


        id_ativo_origem = ValidacaoAtivo.id_positivo(id_ativo_origem)

        if id_ativo_origem == self.id:

            raise ValueError(
                "Um ativo não pode depender "
                "de si mesmo."
            )


        # ====================================================
        # CONVERSÃO DA ESCALA PARA O PESO DA MATRIZ A
        # ====================================================

        valor_nist = nivel.value

        peso = (
            valor_nist / 20
        )


        # ====================================================
        # VERIFICA DUPLICIDADE
        # ====================================================

        for dependencia in self.dependencias:

            if (
                dependencia[
                    "id_ativo_origem"
                ]
                == id_ativo_origem
            ):

                raise ValueError(
                    "A dependência já foi adicionada."
                )


        # ====================================================
        # VERIFICA SOMA DOS PESOS
        # ====================================================

        soma_atual = sum(
            dependencia["peso"]
            for dependencia
            in self.dependencias
        )


        if soma_atual + peso >= 1:

            raise ValueError(
                "A soma dos pesos das dependências "
                "deve permanecer menor que 1."
            )


        # ====================================================
        # ARMAZENA A DEPENDÊNCIA
        # ====================================================

        self.dependencias.append(
            {
                "id_ativo_origem":
                    id_ativo_origem,

                "nivel":
                    nivel.name,

                "valor_nist":
                    valor_nist,

                "peso":
                    peso
            }
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
            "Notebook",
            vulnerabilidades
        )

        self.processador = processador


    @property
    def processador(self):
        return self._processador

    @processador.setter
    def processador(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._processador = ValidacaoAtivo.texto(valor, "Processador")

    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Processador: {self.processador}"
        )


    # --------------------------------------------------------
    # Notebook -> dicionário
    # --------------------------------------------------------

    def to_dict(self):

        dados = super().to_dict()

        dados["processador"] = (
            self.processador
        )

        return dados


    # --------------------------------------------------------
    # Dicionário -> Notebook
    # --------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        dados,
        vulnerabilidades
    ):

        ativo = cls(
            dados["id"],
            dados["nome"],
            dados["responsavel"],
            dados["setor"],
            vulnerabilidades,
            dados["processador"]
        )

        ativo.dependencias = list(
            dados.get(
                "dependencias",
                []
            )
        )

        return ativo


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
            "Servidor",
            vulnerabilidades
        )

        self.servico = servico


    @property
    def servico(self):
        return self._servico

    @servico.setter
    def servico(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._servico = ValidacaoAtivo.texto(valor, "Serviço")

    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Serviço: {self.servico}"
        )


    # --------------------------------------------------------
    # Servidor -> dicionário
    # --------------------------------------------------------

    def to_dict(self):

        dados = super().to_dict()

        dados["servico"] = (
            self.servico
        )

        return dados


    # --------------------------------------------------------
    # Dicionário -> Servidor
    # --------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        dados,
        vulnerabilidades
    ):

        ativo = cls(
            dados["id"],
            dados["nome"],
            dados["responsavel"],
            dados["setor"],
            vulnerabilidades,
            dados["servico"]
        )

        ativo.dependencias = list(
            dados.get(
                "dependencias",
                []
            )
        )

        return ativo


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
            "Roteador",
            vulnerabilidades
        )

        self.endereco_ip = endereco_ip


    @property
    def endereco_ip(self):
        return self._endereco_ip

    @endereco_ip.setter
    def endereco_ip(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._endereco_ip = ValidacaoAtivo.endereco_ip(valor)

    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"Endereço IP: {self.endereco_ip}"
        )


    # --------------------------------------------------------
    # Roteador -> dicionário
    # --------------------------------------------------------

    def to_dict(self):

        dados = super().to_dict()

        dados["endereco_ip"] = (
            self.endereco_ip
        )

        return dados


    # --------------------------------------------------------
    # Dicionário -> Roteador
    # --------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        dados,
        vulnerabilidades
    ):

        ativo = cls(
            dados["id"],
            dados["nome"],
            dados["responsavel"],
            dados["setor"],
            vulnerabilidades,
            dados["endereco_ip"]
        )

        ativo.dependencias = list(
            dados.get(
                "dependencias",
                []
            )
        )

        return ativo


# ============================================================
# APLICAÇÃO WEB
# ============================================================

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


    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, valor):
        # Valida antes de alterar: uma entrada inválida preserva o valor antigo.
        self._url = ValidacaoAtivo.url(valor)

    def exibir_ativo(self):

        super().exibir_ativo()

        print(
            f"URL: {self.url}"
        )


    # --------------------------------------------------------
    # AplicacaoWeb -> dicionário
    # --------------------------------------------------------

    def to_dict(self):

        dados = super().to_dict()

        dados["url"] = (
            self.url
        )

        return dados


    # --------------------------------------------------------
    # Dicionário -> AplicacaoWeb
    # --------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        dados,
        vulnerabilidades
    ):

        ativo = cls(
            dados["id"],
            dados["nome"],
            dados["responsavel"],
            dados["setor"],
            vulnerabilidades,
            dados["url"]
        )

        ativo.dependencias = list(
            dados.get(
                "dependencias",
                []
            )
        )

        return ativo