# S3_19 — Backend e Persistência de Dados

## Modelo Entidade-Relacionamento

Para esta atividade foi desenvolvido um banco de dados relacional simples para armazenar ativos de TI.

A entidade principal é `ATIVO`.

### Entidade ATIVO

A entidade possui os seguintes atributos:

- `id`: identificador único do ativo;
- `nome`: nome ou hostname do ativo;
- `tipo`: tipo do ativo;
- `responsavel`: pessoa responsável pelo ativo;
- `setor`: setor ao qual o ativo pertence.

Representação:

```text
+---------------------------+
|           ATIVO           |
+---------------------------+
| PK id                     |
| nome                      |
| tipo                      |
| responsavel               |
| setor                     |
+---------------------------+
```

O campo `id` é a chave primária da tabela e identifica cada ativo de maneira única.

Neste protótipo foi utilizada apenas uma entidade porque o objetivo principal é demonstrar a integração entre API REST, operações CRUD e persistência em banco de dados relacional.

## Modelo relacional

A entidade é convertida para a seguinte relação:

```text
ATIVO(
    id,
    nome,
    tipo,
    responsavel,
    setor
)
```

Onde:

```text
PK: id
```

## Arquitetura utilizada

A aplicação segue uma arquitetura cliente-servidor simplificada:

```text
Cliente
  ↓
Requisição HTTP
  ↓
API FastAPI
  ↓
SQL
  ↓
Banco SQLite
```

O cliente envia requisições HTTP para a API.

A API processa a requisição e executa operações SQL sobre o banco SQLite.

Os dados são retornados ao cliente no formato JSON.

## Operações CRUD

A API implementa:

```text
CREATE → POST /ativos

READ   → GET /ativos
         GET /ativos/{id}

UPDATE → PUT /ativos/{id}

DELETE → DELETE /ativos/{id}
```

Dessa maneira, todas as operações básicas de persistência exigidas na atividade são contempladas.