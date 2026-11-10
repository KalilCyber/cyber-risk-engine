from sqlalchemy import (
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from infraestrutura.banco.base import Base


class AtivoDB(Base):
    __tablename__ = "ativos"

    # Identificador único do ativo
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    # Atributos comuns a todos os ativos
    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    responsavel: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    setor: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    # Atributos específicos das subclasses
    processador: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    servico: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    endereco_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )

    url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True
    )

    associacoes_vulnerabilidades: Mapped[
        list["AtivoVulnerabilidadeDB"]
    ] = relationship(
        back_populates="ativo"
    )


class VulnerabilidadeDB(Base):
    __tablename__ = "vulnerabilidades"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    descricao: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    categoria: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    severidade: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    cve_id: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True
    )

    cwe_id: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True
    )

    cvss_vector: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    cvss_version: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    associacoes_ativos: Mapped[
        list["AtivoVulnerabilidadeDB"]
    ] = relationship(
        back_populates="vulnerabilidade"
    )

class AtivoVulnerabilidadeDB(Base):
    __tablename__ = "ativo_vulnerabilidades"

    ativo_id: Mapped[int] = mapped_column(
        ForeignKey("ativos.id", ondelete="CASCADE"),
        primary_key=True
    )

    vulnerabilidade_id: Mapped[int] = mapped_column(
        ForeignKey(
            "vulnerabilidades.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    ativo: Mapped["AtivoDB"] = relationship(
        back_populates="associacoes_vulnerabilidades"
    )

    vulnerabilidade: Mapped["VulnerabilidadeDB"] = relationship(
        back_populates="associacoes_ativos"
    )

    
class DependenciaDB(Base):
    __tablename__ = "dependencias"

    __table_args__ = (
        CheckConstraint(
            "ativo_destino_id <> ativo_origem_id",
            name="ck_dependencias_sem_autorreferencia"
        ),
        CheckConstraint(
            "peso >= 0 AND peso < 1",
            name="ck_dependencias_peso_valido"
        ),
    )

    # Ativo que recebe o risco
    ativo_destino_id: Mapped[int] = mapped_column(
        ForeignKey("ativos.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Ativo que transmite o risco
    ativo_origem_id: Mapped[int] = mapped_column(
        ForeignKey("ativos.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Classificação da dependência
    nivel: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    # Valor de referência utilizado pelo modelo
    valor_nist: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # Peso utilizado na matriz A
    peso: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
