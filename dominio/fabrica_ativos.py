from dominio.ativos import (
    Notebook,
    Servidor,
    Roteador,
    AplicacaoWeb
)

class FabricaAtivos:

    @staticmethod
    def criar(
        tipo,
        id,
        nome,
        responsavel,
        setor,
        vulnerabilidades,
        **dados_especificos
    ):
        
        if tipo == "Notebook":

            return Notebook(
                id,
                nome,
                responsavel,
                setor,
                vulnerabilidades,
                dados_especificos["processador"]
            )
        
        if tipo == "Servidor":

            return Servidor(
                id,
                nome,
                responsavel,
                setor,
                vulnerabilidades,
                dados_especificos["servico"]
            )
        
        if tipo == "Roteador":

            return Roteador(
                id,
                nome,
                responsavel,
                setor,
                vulnerabilidades,
                dados_especificos["endereco_ip"]
            )
        
        if tipo == "AplicacaoWeb":

            return AplicacaoWeb(
                id,
                nome,
                responsavel,
                setor,
                vulnerabilidades,
                dados_especificos["url"]
            )
        
        raise ValueError(
            f"Tipo de ativo inválido: {tipo}"
        )


  # ========================================================
    # CRIAR ATIVO A PARTIR DE DICIONÁRIO
    # ========================================================

    @staticmethod

    def criar_de_dict(
        dados,
        vulnerabilidades
    ):

        tipos = {
            "Notebook": Notebook,
            "Servidor": Servidor,
            "Roteador": Roteador,
            "AplicacaoWeb": AplicacaoWeb
        }


        tipo = dados.get(
            "tipo"
        )


        classe_ativo = tipos.get(
            tipo
        )


        if classe_ativo is None:

            raise ValueError(
                f"Tipo de ativo inválido: {tipo}"
            )


        return classe_ativo.from_dict(
            dados,
            vulnerabilidades
        )