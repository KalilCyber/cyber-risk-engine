## Arquitetura do Projeto

A aplicação foi organizada em camadas para separar responsabilidades e reduzir o acoplamento entre os diferentes componentes do sistema.

A estrutura principal é:

```text
cyber-risk-engine/
│
├── dominio/
│   ├── ativos.py
│   ├── vulnerabilidades.py
│   └── enums.py
│
├── servicos/
│   ├── inventario.py
│   ├── modelo_risco.py
│   └── servico_cve.py
│
├── infraestrutura/
│   └── persistencia_json.py
│
├── interface/
│   └── cli/
│       ├── menu_base.py
│       ├── menu_principal.py
│       ├── menu_ativos.py
│       ├── menu_vulnerabilidades.py
│       └── menu_risco.py
│
├── tests/
│
├── ativos.json
├── main.py
├── requirements.txt
└── teste_modelo_risco.py
```

### Camada de Domínio

A pasta `dominio/` contém as classes e conceitos centrais do Cyber Risk Engine.

- `ativos.py`: contém a classe base `Ativo` e suas subclasses `Notebook`, `Servidor`, `Roteador` e `AplicacaoWeb`.
- `vulnerabilidades.py`: contém a classe `Vulnerabilidade` e suas regras relacionadas a severidade, status e identificação.
- `enums.py`: contém os enumeradores utilizados pelo domínio, como os status de tratamento e os níveis de dependência.

Essa camada representa os objetos e regras fundamentais do problema e não é responsável pela persistência dos dados ou pela interação com o usuário.

### Camada de Serviços

A pasta `servicos/` concentra operações e regras utilizadas pela aplicação.

- `inventario.py`: gerencia os ativos, vulnerabilidades, consultas, atualizações, remoções e associações entre objetos.
- `modelo_risco.py`: implementa o modelo matemático de análise de risco, incluindo a matriz de incidência `M`, vetor de severidades `v`, risco próprio `b = Mv`, matriz de dependências `A` e risco efetivo por meio de `(I - A)x = b`.
- `servico_cve.py`: realiza consultas à API da NVD para obtenção de informações de vulnerabilidades, como CVE, CWE e CVSS.

### Camada de Infraestrutura

A pasta `infraestrutura/` contém os recursos responsáveis pela comunicação com mecanismos externos de armazenamento.

- `persistencia_json.py`: realiza a serialização dos objetos para JSON e a reconstrução dos objetos quando os dados são carregados.

O arquivo `ativos.json` é utilizado atualmente como mecanismo de persistência da aplicação.

### Camada de Interface

A pasta `interface/cli/` contém a interface de linha de comando utilizada pelo usuário.

Ela é dividida em menus específicos:

- `menu_principal.py`: coordena o acesso às funcionalidades principais.
- `menu_ativos.py`: interface para gerenciamento dos ativos.
- `menu_vulnerabilidades.py`: interface para gerenciamento das vulnerabilidades.
- `menu_risco.py`: interface para dependências e análise de risco.
- `menu_base.py`: reúne comportamentos compartilhados pelos menus.

### Fluxo entre as camadas

A aplicação segue, de forma simplificada, o seguinte fluxo:

```text
Usuário
   │
   ▼
Interface CLI
   │
   ▼
Serviços
   │
   ├────► Domínio
   │
   └────► Infraestrutura / Persistência
```

O arquivo `main.py` funciona como ponto de inicialização da aplicação. Ele cria e conecta os objetos necessários, carregando a persistência, construindo o inventário, inicializando o serviço de consulta de CVEs e iniciando a interface principal.

Essa organização permite que as diferentes responsabilidades do sistema evoluam de forma independente e prepara a aplicação para as próximas etapas, como testes automatizados, disponibilização de uma interface HTTP e execução em containers Docker.