import json

from dominio.ativos import Notebook, Servidor, Roteador, AplicacaoWeb
from dominio.vulnerabilidades import Vulnerabilidade
from dominio.repositorio_ativos import RepositorioAtivos


class Persistencia(RepositorioAtivos):

    def __init__(
        self,
        arquivo_dados="ativos.json"
    ):
        self.arquivo_dados = arquivo_dados


    # ========================================================
    # OBJETO ATIVO -> DICIONÁRIO
    # ========================================================

    def converter_para_dict(self, ativo):

        vulnerabilidades = []

        for vulnerabilidade in ativo.vulnerabilidades:

            vulnerabilidades.append(
                vulnerabilidade.para_dict()
            )


        dados = {
            "id": ativo.id,
            "nome": ativo.nome,
            "responsavel": ativo.responsavel,
            "setor": ativo.setor,
            "vulnerabilidades": vulnerabilidades,
            "dependencias": ativo.dependencias
        }


        if isinstance(ativo, Notebook):

            dados["tipo"] = "Notebook"
            dados["processador"] = ativo.processador


        elif isinstance(ativo, Servidor):

            dados["tipo"] = "Servidor"
            dados["servico"] = ativo.servico


        elif isinstance(ativo, Roteador):

            dados["tipo"] = "Roteador"
            dados["endereco_ip"] = ativo.endereco_ip

        elif isinstance(ativo, AplicacaoWeb):

            dados["tipo"] = "AplicacaoWeb"
            dados["url"] = ativo.url


        return dados


    # ========================================================
    # SALVAR
    # ========================================================

    def salvar(self, ativos):

        dados = []


        for ativo in ativos:

            dados.append(
                self.converter_para_dict(
                    ativo
                )
            )


        with open(
            self.arquivo_dados,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                indent=4,
                ensure_ascii=False
            )


        print(
            "Ativos salvos com sucesso!"
        )


    # ========================================================
    # CARREGAR
    # ========================================================

    def carregar(self):

        ativos = []

        catalogo_ids = {}
        catalogo_cves = {}


        try:

            with open(
                self.arquivo_dados,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(
                    arquivo
                )


        except FileNotFoundError:

            return ativos


        except json.JSONDecodeError as erro:

            raise ValueError(
                f"O arquivo JSON está inválido: {erro}"
            )


        # O Trabalho 2 exige uma lista de objetos JSON.
        if not isinstance(dados, list):

            raise ValueError(
                "O arquivo JSON deve possuir uma lista de ativos."
            )

# PERCORRE OS ATIVOS DO JSON
  

        for item in dados:

            vulnerabilidades = []

 # RECONSTRUÇÃO DAS VULNERABILIDADES
  

            for dados_vulnerabilidade in item.get(
                "vulnerabilidades",
                []
            ):

                vulnerabilidade = (
                    Vulnerabilidade.de_dict(
                        dados_vulnerabilidade
                )
            )


                id_vulnerabilidade = (
                    vulnerabilidade.id
            )


            # ========================================================
            # VALIDAÇÃO POR ID INTERNO
            # ========================================================

                if (
                    id_vulnerabilidade
                    in catalogo_ids
                ):

                    vulnerabilidade_existente = (
                        catalogo_ids[
                            id_vulnerabilidade
                    ]
                 )


                    if not (
                        vulnerabilidade_existente
                        .possui_mesmos_dados(
                            vulnerabilidade
                        )
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


            # ========================================================
            # VALIDAÇÃO POR CVE
            # ========================================================

            if vulnerabilidade.cve_id:

                chave_cve = (
                    vulnerabilidade.cve_id.upper()
                )


                if chave_cve in catalogo_cves:

                    vulnerabilidade_cve = (
                        catalogo_cves[
                            chave_cve
                        ]
                    )


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


            # Cada ativo mantém seu próprio objeto.
            vulnerabilidades.append(
                vulnerabilidade
            )


            # ====================================================
            # RECONSTRUÇÃO DO ATIVO
            # ====================================================

            tipo = item["tipo"]


            if tipo == "Notebook":

                ativo = Notebook(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    vulnerabilidades,
                    item["processador"]
                )


            elif tipo == "Servidor":

                ativo = Servidor(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    vulnerabilidades,
                    item["servico"]
                )


            elif tipo == "Roteador":

                ativo = Roteador(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    vulnerabilidades,
                    item["endereco_ip"]
                )


            elif tipo == "AplicacaoWeb":

                ativo = AplicacaoWeb(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    vulnerabilidades,
                    item.get("url", "URL não informada")
                )


            else:

                raise ValueError(
                    f"Tipo de ativo desconhecido: {tipo}"
                )

          # Recupera as dependências do ativo  
            
            ativo.dependencias = item.get(
                "dependencias",
                []
            )

            ativos.append(
                ativo
            )


        return ativos 