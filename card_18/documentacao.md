# S3_18 — APIs REST e Testes de Integração

## 1. Objetivo

Esta atividade apresenta o projeto e a documentação de uma API REST para gerenciamento de ativos de TI.

A API permite realizar as operações básicas de CRUD:

- cadastrar ativos;
- consultar ativos;
- atualizar ativos;
- remover ativos.

A comunicação utiliza HTTP e JSON como formato de troca de dados.

---

# 2. Recurso principal

O principal recurso utilizado pela API é:

`ativos`

Um ativo representa um equipamento ou recurso de tecnologia cadastrado no sistema.

Exemplo de representação JSON:

```json
{
    "id": 1,
    "nome": "Servidor Principal",
    "tipo": "Servidor",
    "responsavel": "Carlos",
    "setor": "TI"
}
```

---

# 3. Endereço base da API

Durante a execução local:

`http://localhost:8000`

Todos os endpoints são acessados a partir desse endereço.

---

# 4. Endpoints

## GET /ativos

Retorna a lista de todos os ativos cadastrados.

### Requisição

```http
GET /ativos
```

### Resposta esperada

Status:

`200 OK`

Exemplo:

```json
[
    {
        "id": 1,
        "nome": "Servidor Principal",
        "tipo": "Servidor",
        "responsavel": "Carlos",
        "setor": "TI"
    }
]
```

---

## GET /ativos/{id}

Consulta um ativo específico utilizando seu identificador.

Exemplo:

```http
GET /ativos/1
```

### Resposta quando encontrado

Status:

`200 OK`

```json
{
    "id": 1,
    "nome": "Servidor Principal",
    "tipo": "Servidor",
    "responsavel": "Carlos",
    "setor": "TI"
}
```

### Resposta quando não encontrado

Status:

`404 Not Found`

Exemplo:

```json
{
    "erro": "Ativo não encontrado"
}
```

---

# 5. Cadastro de ativo

## POST /ativos

Cadastra um novo ativo.

### Requisição

```http
POST /ativos
```

Body:

```json
{
    "nome": "Notebook Financeiro",
    "tipo": "Notebook",
    "responsavel": "Ana",
    "setor": "Financeiro"
}
```

### Resposta esperada

Status:

`201 Created`

Exemplo:

```json
{
    "id": 2,
    "nome": "Notebook Financeiro",
    "tipo": "Notebook",
    "responsavel": "Ana",
    "setor": "Financeiro"
}
```

O código `201` indica que um novo recurso foi criado com sucesso.

---

# 6. Atualização de ativo

## PUT /ativos/{id}

Atualiza os dados de um ativo existente.

Exemplo:

```http
PUT /ativos/1
```

Body:

```json
{
    "nome": "Servidor Principal Atualizado",
    "tipo": "Servidor",
    "responsavel": "Carlos",
    "setor": "Infraestrutura"
}
```

### Resposta esperada

Status:

`200 OK`

O servidor retorna os dados atualizados.

Caso o ativo não exista:

`404 Not Found`

---

# 7. Remoção de ativo

## DELETE /ativos/{id}

Remove um ativo do sistema.

Exemplo:

```http
DELETE /ativos/1
```

### Resposta esperada

Status:

`204 No Content`

O código `204` indica que a operação foi concluída com sucesso e que não existe conteúdo para retornar.

Caso o ativo não seja encontrado:

`404 Not Found`

---

# 8. Métodos HTTP utilizados

A API utiliza os seguintes métodos:

| Método | Finalidade |
|---|---|
| GET | Consultar recursos |
| POST | Criar um novo recurso |
| PUT | Atualizar um recurso existente |
| DELETE | Remover um recurso |

Esses métodos permitem implementar as operações CRUD da aplicação.

---

# 9. Principais códigos HTTP

## 200 — OK

A requisição foi processada corretamente.

Utilizado principalmente em consultas e atualizações.

## 201 — Created

Um novo recurso foi criado.

Utilizado no cadastro de ativos.

## 204 — No Content

A operação foi concluída, porém não existe conteúdo para retornar.

Utilizado na exclusão.

## 400 — Bad Request

Os dados enviados pelo cliente estão incorretos ou incompletos.

## 404 — Not Found

O recurso solicitado não foi encontrado.

## 500 — Internal Server Error

Ocorreu uma falha interna no servidor.

---

# 10. Estrutura de uma requisição HTTP

Uma requisição pode possuir:

- método HTTP;
- URL;
- headers;
- body.

Exemplo de cadastro:

```http
POST /ativos
Content-Type: application/json
```

Body:

```json
{
    "nome": "Roteador Principal",
    "tipo": "Roteador",
    "responsavel": "Marcos",
    "setor": "Infraestrutura"
}
```

O header:

`Content-Type: application/json`

informa ao servidor que os dados estão sendo enviados no formato JSON.

---

# 11. Testes de integração

Os testes foram organizados utilizando uma coleção do Postman.

Foram preparados testes para:

- listar ativos;
- consultar ativo por ID;
- cadastrar ativo;
- atualizar ativo;
- remover ativo;
- verificar códigos HTTP;
- validar se as respostas possuem formato JSON;
- validar propriedades presentes nas respostas.

A variável `base_url` da coleção possui o valor:

`http://localhost:8000`

Dessa maneira, os endpoints podem utilizar endereços como:

`{{base_url}}/ativos`

---

# 12. Sequência de teste

A sequência sugerida para validação é:

1. executar `GET /ativos`;
2. executar `POST /ativos`;
3. copiar o ID retornado pelo cadastro;
4. executar `GET /ativos/{id}`;
5. executar `PUT /ativos/{id}`;
6. consultar novamente o ativo;
7. executar `DELETE /ativos/{id}`;
8. tentar consultar novamente o mesmo ID para validar o retorno `404`.

Essa sequência permite verificar a integração entre diferentes operações da API.

---

# Conclusão

A arquitetura REST organiza os recursos da aplicação por meio de URLs e utiliza métodos HTTP para representar diferentes operações.

Neste exercício foi projetada uma API para gerenciamento de ativos, utilizando GET, POST, PUT e DELETE.

Também foram definidos os principais códigos HTTP e preparada uma coleção Postman para realização de testes de integração.

Os testes permitem verificar não apenas se o servidor responde, mas também se os códigos HTTP e os dados JSON retornados correspondem ao comportamento esperado.