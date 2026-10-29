
import json
import os
import tempfile

from dominio.vulnerabilidades import Vulnerabilidade
from dominio.repositorio_ativos import RepositorioAtivos
from dominio.fabrica_ativos import FabricaAtivos


class Persistencia(RepositorioAtivos):

    def __init__(self, arquivo_dados="ativos.json"):
        self.arquivo_dados = arquivo_dados

    # ========================================================
    # OBJETO ATIVO -> DICIONÁRIO
    # ========================================================

    def converter_para_dict(self, ativo):
        return ativo.to_dict()

    # ========================================================
    # SALVAR - ESCRITA ATÔMICA
    # ========================================================

    def salvar(self, ativos):
        dados = [
            self.converter_para_dict(ativo)
            for ativo in ativos
        ]

        diretorio = os.path.dirname(
            os.path.abspath(self.arquivo_dados)
        )

        caminho_temporario = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=diretorio,
                prefix=".ativos-",
                suffix=".tmp",
                delete=False
            ) as arquivo:

                caminho_temporario = arquivo.name

                json.dump(
                    dados,
                    arquivo,
                    indent=4,
                    ensure_ascii=False
                )

                arquivo.flush()
                os.fsync(arquivo.fileno())

            os.replace(
                caminho_temporario,
                self.arquivo_dados
            )

            caminho_temporario = None

        finally:
            if (
                caminho_temporario
                and os.path.exists(caminho_temporario)
            ):
                os.remove(caminho_temporario)

        print("Ativos salvos com sucesso!")

    # ========================================================
    # CARREGAR
    # ========================================================

    def carregar(self):

        ativos = []

        # Catálogos para validação entre registros
        catalogo_ids = {}
        catalogo_cves = {}

        # ----------------------------------------------------
        # 1. LEITURA DO ARQUIVO JSON
        # ----------------------------------------------------

        try:
            with open(
                self.arquivo_dados,
                "r",
                encoding="utf-8"
            ) as arquivo:
                conteudo = arquivo.read().strip()

            if not conteudo:
                return ativos

            dados = json.loads(conteudo)

        except FileNotFoundError:
            return ativos

        except (
            json.JSONDecodeError,
            UnicodeDecodeError
        ) as erro:
            raise ValueError(
                f"O arquivo JSON está inválido: {erro}"
            ) from erro

        if not isinstance(dados, list):
            raise ValueError(
                "O arquivo JSON deve possuir uma lista de ativos."
            )

        # ----------------------------------------------------
        # 2. RECONSTRUÇÃO DE TODOS OS ATIVOS
        # ----------------------------------------------------

        ids_ativos = set()

        for indice, item in enumerate(dados, start=1):

            if not isinstance(item, dict):
                raise ValueError(
                    f"Registro {indice}: cada ativo "
                    "deve ser um objeto JSON."
                )

            dados_vulnerabilidades = item.get(
                "vulnerabilidades",
                []
            )

            if not isinstance(dados_vulnerabilidades, list):
                raise ValueError(
                    f"Registro {indice}: vulnerabilidades "
                    "deve ser uma lista."
                )

            vulnerabilidades = []

            # ------------------------------------------------
            # 2.1 RECONSTRUIR VULNERABILIDADES
            # ------------------------------------------------

            for dados_vulnerabilidade in dados_vulnerabilidades:

                try:
                    vulnerabilidade = Vulnerabilidade.from_dict(
                        dados_vulnerabilidade
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                    AttributeError
                ) as erro:
                    raise ValueError(
                        f"Registro {indice}: "
                        f"vulnerabilidade inválida: {erro}"
                    ) from erro

                id_vulnerabilidade = vulnerabilidade.id

                # --------------------------------------------
                # VALIDAÇÃO POR ID INTERNO
                # --------------------------------------------

                if id_vulnerabilidade in catalogo_ids:

                    vulnerabilidade_existente = catalogo_ids[
                        id_vulnerabilidade
                    ]

                    if not vulnerabilidade_existente.possui_mesmos_dados(
                        vulnerabilidade
                    ):
                        raise ValueError(
                            "Dados inconsistentes para a "
                            "vulnerabilidade ID "
                            f"{id_vulnerabilidade}."
                        )

                else:
                    catalogo_ids[
                        id_vulnerabilidade
                    ] = vulnerabilidade

                # --------------------------------------------
                # VALIDAÇÃO POR CVE
                # --------------------------------------------

                if vulnerabilidade.cve_id:

                    chave_cve = vulnerabilidade.cve_id.upper()

                    if chave_cve in catalogo_cves:

                        vulnerabilidade_cve = catalogo_cves[
                            chave_cve
                        ]

                        if (
                            vulnerabilidade_cve.severidade
                            != vulnerabilidade.severidade
                        ):
                            raise ValueError(
                                f"O CVE {vulnerabilidade.cve_id} "
                                "possui severidades diferentes "
                                "no arquivo JSON."
                            )

                    else:
                        catalogo_cves[
                            chave_cve
                        ] = vulnerabilidade

                # Cada ativo mantém sua própria instância
                vulnerabilidades.append(
                    vulnerabilidade
                )

            # ------------------------------------------------
            # 2.2 RECONSTRUIR O ATIVO
            # Fora do for de vulnerabilidades
            # ------------------------------------------------

            try:
                ativo = FabricaAtivos.criar_de_dict(
                    item,
                    vulnerabilidades
                )

            except (
                KeyError,
                TypeError,
                ValueError,
                AttributeError
            ) as erro:
                raise ValueError(
                    f"Registro {indice}: ativo inválido: {erro}"
                ) from erro

            # Não permitir IDs duplicados entre ativos
            if ativo.id in ids_ativos:
                raise ValueError(
                    "ID de ativo duplicado no JSON: "
                    f"{ativo.id}."
                )

            ids_ativos.add(ativo.id)
            ativos.append(ativo)

        # ----------------------------------------------------
        # 3. VALIDAR DEPENDÊNCIAS
        # Somente após reconstruir TODOS os ativos
        # ----------------------------------------------------

        for ativo in ativos:

            if not isinstance(ativo.dependencias, list):
                raise ValueError(
                    "Dependências inválidas no ativo "
                    f"ID {ativo.id}."
                )

            origens = set()
            soma_pesos = 0.0

            for dependencia in ativo.dependencias:

                if not isinstance(dependencia, dict):
                    raise ValueError(
                        "Dependência inválida no ativo "
                        f"ID {ativo.id}."
                    )

                origem = dependencia.get(
                    "id_ativo_origem"
                )

                # Todos os IDs já estão no conjunto
                if (
                    type(origem) is not int
                    or origem not in ids_ativos
                ):
                    raise ValueError(
                        f"Ativo ID {ativo.id}: dependência "
                        "aponta para ID inexistente/inválido: "
                        f"{origem}."
                    )

                if (
                    origem == ativo.id
                    or origem in origens
                ):
                    raise ValueError(
                        f"Ativo ID {ativo.id}: dependência "
                        "repetida ou para si mesmo."
                    )

                origens.add(origem)

                try:
                    peso = float(
                        dependencia["peso"]
                    )

                except (
                    KeyError,
                    ValueError,
                    TypeError
                ) as erro:
                    raise ValueError(
                        f"Ativo ID {ativo.id}: "
                        "peso de dependência inválido."
                    ) from erro

                if not 0 <= peso < 1:
                    raise ValueError(
                        f"Ativo ID {ativo.id}: "
                        "peso fora do intervalo [0, 1)."
                    )

                soma_pesos += peso

            if soma_pesos >= 1:
                raise ValueError(
                    f"Ativo ID {ativo.id}: soma dos pesos "
                    "deve ser menor que 1."
                )

        # ----------------------------------------------------
        # 4. RETORNAR O INVENTÁRIO RECONSTRUÍDO
        # ----------------------------------------------------

        return ativos
