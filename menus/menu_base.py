class MenuBase:

    def __init__(self, inventario, persistencia):
        self.inventario = inventario
        self.persistencia = persistencia


    def ler_campo_obrigatorio(self, mensagem):

        while True:

            valor = input(
                mensagem
            ).strip()

            if valor:
                return valor

            print(
                "Este campo não pode ficar vazio."
            )


    def ler_responsavel(
        self,
        mensagem,
        permitir_vazio=False
    ):

        while True:

            responsavel = input(
                mensagem
            ).strip()


            if (
                permitir_vazio
                and responsavel == ""
            ):
                return None


            if (
                responsavel
                and responsavel.replace(
                    " ",
                    ""
                ).isalpha()
            ):
                return responsavel


            print(
                "Responsável inválido. "
                "Digite apenas letras e espaços."
            )
    
    def resumir_texto(self, texto, limite=50):
        if not texto:
            return ""

        texto = str(texto).strip()

        if len(texto) <= limite:
            return texto

        return texto[:limite - 3].rstrip() + "..."


    def salvar_dados(self):

        self.persistencia.salvar(
            self.inventario.listar_ativos()
        )