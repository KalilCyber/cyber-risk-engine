import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CAMINHO_BANCO = BASE_DIR / "ativos.db"
CAMINHO_SCRIPT_SQL = BASE_DIR / "banco.sql"


app = FastAPI(
    title="API de Ativos",
    description=(
        "API REST para gerenciamento "
        "de ativos de TI."
    ),
    version="1.0.0"
)


# ============================================================
# MODELO DE ENTRADA
# ============================================================

class AtivoEntrada(BaseModel):
    nome: str
    tipo: str
    responsavel: str
    setor: str


# ============================================================
# BANCO DE DADOS
# ============================================================

def conectar_banco():
    conexao = sqlite3.connect(
        CAMINHO_BANCO
    )

    conexao.row_factory = sqlite3.Row

    return conexao


def inicializar_banco():

    with open(
        CAMINHO_SCRIPT_SQL,
        "r",
        encoding="utf-8"
    ) as arquivo:

        script_sql = arquivo.read()


    conexao = conectar_banco()

    try:

        conexao.executescript(
            script_sql
        )

        conexao.commit()

    finally:

        conexao.close()


inicializar_banco()


# ============================================================
# ROTA INICIAL
# ============================================================

@app.get("/")
def inicio():

    return {
        "mensagem": "API de Ativos funcionando"
    }


# ============================================================
# LISTAR ATIVOS
# ============================================================

@app.get("/ativos")
def listar_ativos():

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            SELECT
                id,
                nome,
                tipo,
                responsavel,
                setor
            FROM ativos
            ORDER BY id
            """
        )

        ativos = [
            dict(linha)
            for linha in cursor.fetchall()
        ]

        return ativos

    finally:

        conexao.close()


# ============================================================
# CONSULTAR ATIVO POR ID
# ============================================================

@app.get("/ativos/{id_ativo}")
def consultar_ativo(id_ativo: int):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            SELECT
                id,
                nome,
                tipo,
                responsavel,
                setor
            FROM ativos
            WHERE id = ?
            """,
            (id_ativo,)
        )

        ativo = cursor.fetchone()

    finally:

        conexao.close()


    if ativo is None:

        return JSONResponse(
            status_code=404,
            content={
                "erro": "Ativo não encontrado"
            }
        )


    return dict(ativo)


# ============================================================
# CADASTRAR ATIVO
# ============================================================

@app.post(
    "/ativos",
    status_code=201
)
def cadastrar_ativo(
    ativo: AtivoEntrada
):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            INSERT INTO ativos (
                nome,
                tipo,
                responsavel,
                setor
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ativo.nome,
                ativo.tipo,
                ativo.responsavel,
                ativo.setor
            )
        )

        conexao.commit()

        id_ativo = cursor.lastrowid

    finally:

        conexao.close()


    return {
        "id": id_ativo,
        "nome": ativo.nome,
        "tipo": ativo.tipo,
        "responsavel": ativo.responsavel,
        "setor": ativo.setor
    }


# ============================================================
# ATUALIZAR ATIVO
# ============================================================

@app.put("/ativos/{id_ativo}")
def atualizar_ativo(
    id_ativo: int,
    ativo: AtivoEntrada
):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            SELECT id
            FROM ativos
            WHERE id = ?
            """,
            (id_ativo,)
        )


        if cursor.fetchone() is None:

            return JSONResponse(
                status_code=404,
                content={
                    "erro":
                        "Ativo não encontrado"
                }
            )


        conexao.execute(
            """
            UPDATE ativos
            SET
                nome = ?,
                tipo = ?,
                responsavel = ?,
                setor = ?
            WHERE id = ?
            """,
            (
                ativo.nome,
                ativo.tipo,
                ativo.responsavel,
                ativo.setor,
                id_ativo
            )
        )

        conexao.commit()

    finally:

        conexao.close()


    return {
        "id": id_ativo,
        "nome": ativo.nome,
        "tipo": ativo.tipo,
        "responsavel": ativo.responsavel,
        "setor": ativo.setor
    }


# ============================================================
# REMOVER ATIVO
# ============================================================

@app.delete(
    "/ativos/{id_ativo}",
    status_code=204
)
def remover_ativo(id_ativo: int):

    conexao = conectar_banco()

    try:

        cursor = conexao.execute(
            """
            SELECT id
            FROM ativos
            WHERE id = ?
            """,
            (id_ativo,)
        )


        if cursor.fetchone() is None:

            return JSONResponse(
                status_code=404,
                content={
                    "erro":
                        "Ativo não encontrado"
                }
            )


        conexao.execute(
            """
            DELETE FROM ativos
            WHERE id = ?
            """,
            (id_ativo,)
        )

        conexao.commit()

    finally:

        conexao.close()


    return Response(
        status_code=204
    )