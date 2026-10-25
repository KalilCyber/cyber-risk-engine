import requests
from datetime import datetime, timedelta, timezone

class ServicoCVE:
    URL_BASE = ("https://services.nvd.nist.gov/"
                "rest/json/cves/2.0")
    
    def normalizar_termo(self, termo):
        termos_conhecidos = {
            "injeção de sql": "SQL Injection",
            "injecao de sql": "SQL Injection",
            "sql injection": "SQL Injection",

            "xss": "Cross Site Scripting",
            "cross site scripting": "Cross Site Scripting",

            "execução remota de código":
                "Remote Code Execution",

            "execucao remota de codigo":
                "Remote Code Execution",

            "rce":
                "Remote Code Execution",

            "travessia de diretório":
                "Path Traversal",

            "travessia de diretorio":
                "Path Traversal",

            "path traversal":
                "Path Traversal",
        }


        termo_normalizado = termo.strip().lower()


        return termos_conhecidos.get(
                termo_normalizado,termo
            )


 # PESQUISA CVEs PELO NOME

    def pesquisar_por_nome(
        self,
        termo,
        limite=5
    ):

        termo_pesquisa = self.normalizar_termo(
            termo
        )


        # Data atual em UTC
        data_final = datetime.now(
            timezone.utc
        )

        # NVD limita intervalos de datas.
        # Vamos pesquisar os últimos 120 dias.
        data_inicial = (
            data_final - timedelta(days=120)
        )


        formato_data = (
            "%Y-%m-%dT%H:%M:%S.000Z"
        )


        parametros = {
            "keywordSearch": termo_pesquisa,

            "pubStartDate":
                data_inicial.strftime(
                    formato_data
                ),

            "pubEndDate":
                data_final.strftime(
                    formato_data
                ),

            "resultsPerPage": 100
        }


        try:

            resposta = requests.get(
                self.URL_BASE,
                params=parametros,
                timeout=20
            )

            resposta.raise_for_status()


        except requests.exceptions.Timeout:

            raise ConnectionError(
                "A consulta à NVD demorou demais."
            )


        except requests.exceptions.ConnectionError:

            raise ConnectionError(
                "Não foi possível conectar à NVD."
            )


        except requests.exceptions.HTTPError as erro:

            raise ConnectionError(
                f"Erro retornado pela NVD: {erro}"
            )


        dados = resposta.json()

        resultados = []


        for item in dados.get(
            "vulnerabilities",
            []
        ):

            cve = item.get(
                "cve",
                {}
            )


            resultado = self._converter_cve(
                cve
            )


            # Aceita somente CVSS moderno
            if resultado["cvss"] is None:
                continue


            resultados.append(
                resultado
            )


            if len(resultados) >= limite:
                break


        return resultados


        # CONVERTE RESPOSTA DA NVD

    def _converter_cve(
            self,
            cve
        ):

            return {
                "cve_id":
                    cve.get(
                        "id",
                        "CVE não informado"
                    ),

                "publicado":
                    cve.get(
                        "published",
                        "Data não informada"
                    ),

                "descricao":
                    self._obter_descricao(
                        cve
                    ),

                "cwe_id":
                    self._obter_cwe(
                        cve
                    ),

                "cvss":
                    self._obter_cvss(
                        cve
                    )
            }

        # DESCRIÇÃO

    def _obter_descricao(
            self,
            cve
        ):

            descricoes = cve.get(
                "descriptions",
                []
            )


            for descricao in descricoes:

                if descricao.get("lang") == "en":

                    return descricao.get(
                        "value",
                        "Descrição não disponível."
                    )


            return "Descrição não disponível."


        # CWE

    def _obter_cwe(
            self,
            cve
        ):

            weaknesses = cve.get(
                "weaknesses",
                []
            )


            for weakness in weaknesses:

                for descricao in weakness.get(
                    "description",
                    []
                ):

                    valor = descricao.get(
                        "value"
                    )


                    if (
                        valor
                        and valor.startswith("CWE-")
                    ):

                        return valor


            return None


        # CVSS

    def _obter_cvss(
        self,
        cve
):

        metricas = cve.get(
        "metrics", {})


        versoes = [
        "cvssMetricV40",
        "cvssMetricV31"]


        for versao in versoes:

            dados_metrica = metricas.get(
                versao
            )


            if not dados_metrica:
                continue


            cvss_data = dados_metrica[0].get(
                "cvssData",
                {}
            )


            return {
                "score":
                    cvss_data.get(
                        "baseScore"
                    ),

                "severidade":
                    cvss_data.get(
                        "baseSeverity"
                    ),

                "versao":
                    cvss_data.get(
                        "version"
                    ),

                "vetor":
                    cvss_data.get(
                        "vectorString"
                    )
            }


        return None
    

if __name__ == "__main__":

    servico = ServicoCVE()

    termo = input(
        "Digite uma vulnerabilidade: "
    )

    try:

        resultados = servico.pesquisar_por_nome(
            termo
        )

        if not resultados:

            print(
                "Nenhuma vulnerabilidade encontrada."
            )

        for indice, resultado in enumerate(
            resultados,
            start=1
        ):

            print(
                "\n----------------------------"
            )

            print(
                f"{indice} - "
                f"{resultado['cve_id']}"
            )

            print(
                f"CWE: "
                f"{resultado['cwe_id'] or 'Não informado'}"
            )

            print(
                f"Descrição: "
                f"{resultado['descricao']}"
            )

            cvss = resultado["cvss"]


            if cvss:

                print(
                    f"CVSS: {cvss['score']}"
                )

                print(
                    f"Versão: {cvss['versao']}"
                )

                print(
                    f"Vetor: {cvss['vetor']}"
                )

            else:

                print(
                    "CVSS não disponível."
                )


    except ConnectionError as erro:

        print(
            f"Erro: {erro}"
        )