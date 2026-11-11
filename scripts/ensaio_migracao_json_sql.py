
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import text

from math import isclose, isfinite

from servicos.inventario import Inventario
from servicos.modelo_risco import ModeloRisco

from infraestrutura.persistencia_json import Persistencia
from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy,
)


def fotografia(ativos):
    """Prepara os dados para uma comparação independente da ordem."""

    resultado = {}

    for ativo in ativos:
        dados = ativo.to_dict()

        dados["vulnerabilidades"] = sorted(
            dados["vulnerabilidades"],
            key=lambda vuln: vuln["id"]
        )

        dados["dependencias"] = sorted(
            dados["dependencias"],
            key=lambda dep: dep["id_ativo_origem"]
        )

        if ativo.id in resultado:
            raise ValueError(
                f"ID de ativo duplicado: {ativo.id}"
            )

        resultado[ativo.id] = dados

    return resultado


def calcular_riscos_por_ativo(ativos):
    """Calcula os riscos próprios e efetivos por ID."""

    inventario = Inventario(ativos)

    modelo = ModeloRisco(inventario)

    # Executa o modelo matemático completo.
    riscos_efetivos = modelo.calcular_risco_efetivo()

    resultados = {}

    for indice, ativo in enumerate(modelo.ativos):
        resultados[ativo.id] = {
            "risco_proprio": float(
                modelo.vetor_b[indice]
            ),
            "risco_efetivo": float(
                riscos_efetivos[indice]
            )
        }

    return resultados


def comparar_riscos(ativos_originais, ativos_recuperados):
    """Verifica se a migração preservou os resultados."""

    riscos_antes = calcular_riscos_por_ativo(
        ativos_originais
    )

    riscos_depois = calcular_riscos_por_ativo(
        ativos_recuperados
    )

    if riscos_antes.keys() != riscos_depois.keys():
        raise AssertionError(
            "Os inventários possuem IDs diferentes."
        )

    print("\nComparação dos riscos por ativo:")

    for id_ativo in sorted(riscos_antes):

        antes = riscos_antes[id_ativo]
        depois = riscos_depois[id_ativo]

        for campo in ("risco_proprio", "risco_efetivo"):

            valor_antes = antes[campo]
            valor_depois = depois[campo]

            equivalente = (
                isfinite(valor_antes)
                and isfinite(valor_depois)
                and isclose(
                    valor_antes,
                    valor_depois,
                    rel_tol=1e-9,
                    abs_tol=1e-9
                )
            )

            if not equivalente:
                raise AssertionError(
                    f"Divergência no ativo {id_ativo}, "
                    f"campo {campo}: "
                    f"antes={valor_antes}, "
                    f"depois={valor_depois}"
                )

        print(
            f"Ativo {id_ativo}: "
            f"risco próprio={depois['risco_proprio']:.4f} | "
            f"risco efetivo={depois['risco_efetivo']:.4f}"
        )

    print("\nRESULTADOS MATEMÁTICOS PRESERVADOS!")


def executar_ensaio():
    origem = Path("ativos.json").resolve()

    if not origem.is_file():
        raise FileNotFoundError(
            f"Inventário não encontrado: {origem}"
        )

    # 1. Carrega o inventário original.
    repositorio_json = Persistencia(str(origem))
    ativos_originais = repositorio_json.carregar()

    antes = fotografia(ativos_originais)

    print(f"Ativos no JSON: {len(ativos_originais)}")

    # 2. Cria um SQLite temporário.
    with TemporaryDirectory() as pasta:
        caminho_banco = Path(pasta) / "migracao_teste.db"

        engine = criar_engine_sqlite(caminho_banco)

        try:
            # Apenas o banco temporário usa create_all.
            Base.metadata.create_all(engine)

            repositorio_sql = PersistenciaSQLAlchemy(engine)

            # 3. Salva os dados convertidos.
            repositorio_sql.salvar(ativos_originais)

            # 4. Recupera os dados do SQLite.
            ativos_recuperados = repositorio_sql.carregar()
            depois = fotografia(ativos_recuperados)

            # 5. Confere se houve perda ou alteração.
            if antes != depois:
                ids_diferentes = sorted(
                    id_ativo
                    for id_ativo in set(antes) | set(depois)
                    if antes.get(id_ativo) != depois.get(id_ativo)
                )

                raise AssertionError(
                    "Divergência após a migração. "
                    f"IDs afetados: {ids_diferentes}"
                )
                 
            # Compara os resultados do modelo matemático.
            comparar_riscos(
                ativos_originais,
                ativos_recuperados
            )
            # 6. Confere os registros físicos no banco.
            tabelas = (
                "ativos",
                "vulnerabilidades",
                "ativo_vulnerabilidades",
                "dependencias",
            )

            with engine.connect() as conexao:
                print("\nRegistros gravados no SQLite:")

                for tabela in tabelas:
                    quantidade = conexao.execute(
                        text(f"SELECT COUNT(*) FROM {tabela}")
                    ).scalar_one()

                    print(f"  {tabela}: {quantidade}")

            print("\nMIGRAÇÃO EXPERIMENTAL VALIDADA!")
            print("Os dados recuperados são equivalentes ao JSON.")

        finally:
            engine.dispose()


if __name__ == "__main__":
    executar_ensaio()
