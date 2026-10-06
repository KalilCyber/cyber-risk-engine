import json

from ativos import Notebook, Servidor, Roteador

class Persistencia:

    def __init__(self, arquivo_dados="ativos.json"):
        self.arquivo_dados = arquivo_dados


    def converter_para_dict(self, ativo):

        dados = {
            "id": ativo.id,
            "nome": ativo.nome,
            "responsavel": ativo.responsavel,
            "setor": ativo.setor,
            "vulnerabilidade": ativo.vulnerabilidade
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

        return dados


    def salvar(self, ativos):

        dados = []

        for ativo in ativos:
            dados.append(
                self.converter_para_dict(ativo)
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

        print("Ativos salvos com sucesso!")


    def carregar(self):

        ativos = []

        try:

            with open(self.arquivo_dados,
                "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

        except FileNotFoundError:
            return ativos


        for item in dados:

            tipo = item["tipo"]

            if tipo == "Notebook":

                ativo = Notebook(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    item["vulnerabilidade"],
                    item["processador"]
                )


            elif tipo == "Servidor":

                ativo = Servidor(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    item["vulnerabilidade"],
                    item["servico"]
                )


            elif tipo == "Roteador":

                ativo = Roteador(
                    item["id"],
                    item["nome"],
                    item["responsavel"],
                    item["setor"],
                    item["vulnerabilidade"],
                    item["endereco_ip"]
                )


            else:
                continue


            ativos.append(ativo)


        return ativos

