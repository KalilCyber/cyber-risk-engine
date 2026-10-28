import math

from dominio.ativos import ValidacaoAtivo


class MenuBase:
    def __init__(self, inventario):
        self.inventario = inventario

    def ler_texto(self, mensagem, permitir_vazio=False, tipo="texto"):
        """Repete somente o campo inválido, antes de alterar o inventário."""
        while True:
            valor = input(mensagem).strip()
            if permitir_vazio and valor == "":
                return ""
            try:
                if tipo == "ip":
                    return ValidacaoAtivo.endereco_ip(valor)
                if tipo == "url":
                    return ValidacaoAtivo.url(valor)
                return ValidacaoAtivo.texto(valor, "O campo")
            except ValueError as erro:
                print(erro)

    def ler_campo_obrigatorio(self, mensagem):
        return self.ler_texto(mensagem)

    def ler_responsavel(self, mensagem, permitir_vazio=False):
        # Preserva a regra original do menu para nomes de responsáveis.
        while True:
            valor = input(mensagem).strip()
            if permitir_vazio and not valor:
                return None
            if valor and valor.replace(" ", "").isalpha():
                return valor
            print("Responsável inválido. Digite apenas letras e espaços.")

    def ler_inteiro_positivo(self, mensagem):
        while True:
            entrada = input(mensagem).strip()
            try:
                return ValidacaoAtivo.id_positivo(int(entrada))
            except ValueError:
                print("Informe um número inteiro maior que zero.")

    def ler_opcao(self, mensagem, opcoes, permitir_vazio=False):
        permitidas = tuple(str(opcao).lower() for opcao in opcoes)
        while True:
            valor = input(mensagem).strip().lower()
            if permitir_vazio and valor == "":
                return ""
            if valor in permitidas:
                return valor
            print("Opção inválida. Escolha: " + ", ".join(permitidas) + ".")

    def ler_severidade(self, mensagem, permitir_vazio=False):
        while True:
            entrada = input(mensagem).strip()
            if permitir_vazio and entrada == "":
                return ""
            try:
                valor = float(entrada.replace(",", "."))
                if math.isfinite(valor) and 0 <= valor <= 10:
                    return valor
            except ValueError:
                pass
            print("Informe uma severidade entre 0 e 10.")

    def ler_selecao_cve(self, mensagem, resultados):
        codigos = {item["cve_id"].upper() for item in resultados}
        while True:
            valor = input(mensagem).strip().upper()
            if valor in codigos:
                return valor
            if valor.isascii() and valor.isdecimal():
                if 1 <= int(valor) <= len(resultados):
                    return valor
            print("Escolha um número ou CVE entre os resultados apresentados.")

    def resumir_texto(self, texto, limite=50):
        if not texto:
            return ""
        texto = str(texto).strip()
        if len(texto) <= limite:
            return texto
        return texto[:limite - 3].rstrip() + "..."

    def salvar_dados(self):
        self.inventario.salvar()
