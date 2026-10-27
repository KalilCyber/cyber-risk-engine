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