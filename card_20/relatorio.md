# S3_20 — Redes, Segurança, LGPD e Sustentabilidade

## 1. Introdução

Este relatório apresenta uma análise básica dos aspectos de redes de computadores, segurança da informação, proteção de dados, estatística descritiva e sustentabilidade relacionados a uma aplicação Web de gerenciamento de ativos de TI.

O cenário considerado é uma aplicação na qual usuários acessam uma interface Web para consultar ou administrar ativos cadastrados em um sistema.

A comunicação pode ser representada de forma simplificada como:

```text
Usuário
   ↓
Navegador
   ↓
Rede TCP/IP
   ↓
Servidor Web / API
   ↓
Backend
   ↓
Banco de dados
```

---

# 2. Comunicação da aplicação pela rede

Em uma aplicação Web, o usuário utiliza um navegador para enviar requisições a um servidor.

Essas requisições normalmente utilizam protocolos da camada de aplicação, como HTTP ou HTTPS, que funcionam sobre a arquitetura TCP/IP.

Exemplo:

```text
Navegador
   ↓
HTTP/HTTPS
   ↓
TCP
   ↓
IP
   ↓
Rede
   ↓
Servidor
```

O protocolo IP é responsável pelo endereçamento e encaminhamento dos pacotes entre dispositivos.

Cada dispositivo conectado a uma rede IPv4 possui um endereço, como:

```text
192.168.1.20
```

Esse endereço permite identificar o equipamento dentro da rede.

A máscara de rede ajuda a determinar qual parte do endereço representa a rede e qual parte representa o dispositivo.

Um exemplo comum é:

```text
IP:      192.168.1.20
Máscara: 255.255.255.0
```

Nesse caso, os dispositivos `192.168.1.x` normalmente pertencem à mesma rede lógica.

---

# 3. TCP e UDP

TCP e UDP são protocolos da camada de transporte, porém apresentam características diferentes.

## TCP

O TCP é orientado à conexão e busca fornecer uma comunicação confiável.

Entre suas características estão:

- controle da conexão;
- entrega ordenada;
- retransmissão em caso de perda;
- confirmação de recebimento.

Por isso, é adequado para aplicações em que a integridade dos dados é importante.

Exemplos:

- páginas Web;
- APIs;
- transferência de arquivos;
- acesso a sistemas corporativos.

Uma aplicação Web normalmente utiliza HTTP ou HTTPS sobre TCP.

---

## UDP

O UDP não estabelece uma conexão da mesma forma que o TCP e possui menor quantidade de mecanismos de controle.

Isso reduz a sobrecarga, porém não existe a mesma garantia de entrega e ordenação.

Pode ser utilizado em situações nas quais velocidade e baixa latência são mais importantes do que garantir a entrega de todos os pacotes.

Exemplos:

- transmissão de áudio e vídeo em tempo real;
- alguns jogos online;
- DNS;
- determinadas aplicações de streaming.

---

# 4. Three-Way Handshake

Antes da transmissão de dados em uma conexão TCP, cliente e servidor estabelecem uma conexão.

Esse processo é conhecido como Three-Way Handshake.

A sequência simplificada é:

```text
Cliente                         Servidor

   SYN  ----------------------->

        <------------------- SYN + ACK

   ACK  ----------------------->
```

## Etapa 1 — SYN

O cliente informa ao servidor que deseja iniciar uma conexão.

## Etapa 2 — SYN + ACK

O servidor confirma o recebimento e também solicita a confirmação do cliente.

## Etapa 3 — ACK

O cliente envia a confirmação final.

Depois disso, a conexão TCP pode ser utilizada para a troca de dados.

---

# 5. Comunicação cliente-servidor

No contexto da aplicação analisada, podemos representar uma consulta de ativos desta forma:

```text
Cliente
   ↓
GET /ativos
   ↓
Servidor / API
   ↓
Consulta dados
   ↓
Resposta HTTP
   ↓
JSON
   ↓
Cliente
```

Por exemplo, um cliente poderia realizar:

```http
GET /ativos
```

A API processaria a requisição e retornaria os dados no formato JSON.

Essa arquitetura separa as responsabilidades entre cliente e servidor.

O cliente é responsável principalmente pela apresentação dos dados, enquanto o servidor executa regras de negócio, acesso a dados e controles de segurança.

---

# 6. Autenticação e autorização

Autenticação e autorização possuem objetivos diferentes.

## Autenticação

Autenticação responde à pergunta:

> Quem é o usuário?

Um exemplo comum é:

```text
E-mail
+
Senha
```

Após validar as credenciais, o sistema identifica quem está acessando a aplicação.

---

## Autorização

Autorização responde à pergunta:

> O que esse usuário pode fazer?

Depois da autenticação, o sistema verifica quais recursos e operações estão disponíveis para aquele usuário.

Por exemplo:

```text
Usuário comum
    ↓
Consultar ativos

Analista de segurança
    ↓
Consultar ativos
Cadastrar vulnerabilidades
Atualizar vulnerabilidades

Administrador
    ↓
Consultar
Cadastrar
Atualizar
Excluir
Gerenciar usuários
```

Portanto, um usuário pode estar autenticado e ainda assim não possuir autorização para executar determinada operação.

---

# 7. Princípio do menor privilégio

O princípio do menor privilégio determina que cada usuário deve possuir somente as permissões necessárias para realizar suas atividades.

Uma possível estrutura para a aplicação seria:

| Perfil | Consultar | Cadastrar | Atualizar | Excluir |
|---|---:|---:|---:|---:|
| Visualizador | Sim | Não | Não | Não |
| Analista | Sim | Sim | Sim | Não |
| Administrador | Sim | Sim | Sim | Sim |

Essa estrutura reduz o risco de alterações indevidas ou acidentais.

Por exemplo, um usuário responsável apenas por consultar os ativos não precisa possuir permissão para excluir um equipamento.

---

# 8. Defesa em profundidade

A segurança não deve depender de apenas um mecanismo.

O princípio de defesa em profundidade utiliza diversas camadas de proteção.

Na aplicação analisada, poderiam ser aplicados mecanismos como:

```text
HTTPS
   ↓
Autenticação
   ↓
Autorização
   ↓
Validação de entrada
   ↓
Controle de acesso ao banco
   ↓
Logs
   ↓
Backup
```

Se uma camada falhar, outras ainda podem dificultar ou impedir um ataque.

Também podem ser utilizadas medidas como:

- senhas armazenadas de forma segura;
- limitação de tentativas de autenticação;
- atualização das dependências utilizadas;
- validação dos dados recebidos pela API;
- utilização de consultas parametrizadas;
- monitoramento de eventos;
- backups periódicos.

---

# 9. LGPD e a aplicação

A Lei Geral de Proteção de Dados — LGPD — estabelece regras relacionadas ao tratamento de dados pessoais.

Para analisar sua aplicação, primeiramente é necessário identificar quais informações armazenadas podem estar relacionadas a pessoas.

Um exemplo presente no cadastro de ativos é:

```text
responsável pelo ativo
```

Se o campo permitir identificar uma pessoa física, ele pode representar dado pessoal.

Outros exemplos que poderiam existir futuramente são:

- nome;
- e-mail;
- telefone;
- identificador de usuário;
- endereço IP quando relacionado a uma pessoa identificável.

A aplicação deve evitar armazenar informações pessoais que não sejam necessárias para sua finalidade.

---

# 10. Dados pessoais e dados sensíveis

Dados pessoais são informações relacionadas a uma pessoa natural identificada ou identificável.

Exemplos:

```text
nome
e-mail
telefone
identificadores relacionados ao usuário
```

Dados pessoais sensíveis possuem proteção ainda maior e incluem determinadas informações relacionadas, por exemplo, a saúde, origem racial ou étnica, religião e biometria.

No sistema analisado, não existe necessidade evidente de armazenar dados pessoais sensíveis.

Por isso, esse tipo de informação não deve ser incluído sem uma finalidade legítima e necessidade claramente definida.

---

# 11. Princípios aplicáveis da LGPD

Alguns cuidados importantes para a aplicação são:

## Finalidade

Os dados devem ser coletados para uma finalidade específica.

Por exemplo, o nome do responsável pelo ativo pode ser utilizado para identificar quem administra determinado equipamento.

---

## Necessidade

Somente informações realmente necessárias devem ser armazenadas.

Se o sistema precisa apenas do nome do responsável, não existe motivo para solicitar informações pessoais adicionais sem necessidade.

---

## Segurança

Os dados devem ser protegidos contra acessos não autorizados, alterações indevidas, perda e vazamento.

Algumas medidas são:

- controle de acesso;
- autenticação;
- HTTPS;
- proteção do banco de dados;
- logs de acesso;
- backups;
- atualização dos sistemas.

---

## Controle de acesso

Nem todos os usuários devem visualizar ou modificar todos os dados.

O princípio do menor privilégio auxilia diretamente nesse requisito.

---

# 12. Análise estatística

Para demonstrar estatística descritiva, considere as seguintes quantidades de vulnerabilidades encontradas em seis ativos:

```text
Ativo 1 → 2 vulnerabilidades
Ativo 2 → 4 vulnerabilidades
Ativo 3 → 1 vulnerabilidade
Ativo 4 → 3 vulnerabilidades
Ativo 5 → 1 vulnerabilidade
Ativo 6 → 1 vulnerabilidade
```

Assim, temos:

```text
2, 4, 1, 3, 1, 1
```

---

## Média

A média é:

```text
(2 + 4 + 1 + 3 + 1 + 1) / 6
```

Logo:

```text
12 / 6 = 2
```

A média é:

```text
2 vulnerabilidades por ativo
```

---

## Mediana

Organizando os valores:

```text
1, 1, 1, 2, 3, 4
```

Como existem seis valores, calculamos a média dos dois elementos centrais:

```text
(1 + 2) / 2
```

Logo:

```text
Mediana = 1,5
```

---

## Moda

A moda corresponde ao valor que aparece com maior frequência.

No conjunto:

```text
1, 1, 1, 2, 3, 4
```

o valor `1` aparece três vezes.

Portanto:

```text
Moda = 1
```

---

## Amplitude

Uma medida simples de dispersão é a amplitude.

Calculamos:

```text
maior valor - menor valor
```

Então:

```text
4 - 1 = 3
```

Logo:

```text
Amplitude = 3
```

---

# 13. Interpretação estatística

Os resultados obtidos foram:

| Medida | Resultado |
|---|---:|
| Média | 2 |
| Mediana | 1,5 |
| Moda | 1 |
| Amplitude | 3 |

A média indica que existem aproximadamente duas vulnerabilidades por ativo.

A mediana mostra que metade dos ativos possui até aproximadamente 1,5 vulnerabilidade.

A moda indica que a situação mais comum é encontrar uma vulnerabilidade associada a um ativo.

A amplitude mostra uma diferença de três vulnerabilidades entre o ativo com menor e o ativo com maior quantidade.

Essas medidas podem ajudar a compreender de forma resumida a distribuição das vulnerabilidades do inventário.

---

# 14. Sustentabilidade em sistemas computacionais

Sistemas computacionais também possuem impactos ambientais.

O processamento de dados utiliza energia elétrica, assim como servidores, equipamentos de rede, data centers e sistemas de armazenamento.

Além disso, equipamentos de TI possuem vida útil limitada e seu descarte inadequado pode gerar resíduos eletrônicos.

Algumas práticas que podem contribuir para maior sustentabilidade são:

- evitar armazenamento desnecessário de dados;
- reduzir processamento desnecessário;
- otimizar aplicações;
- dimensionar corretamente servidores;
- consolidar serviços quando possível;
- aumentar a vida útil dos equipamentos;
- realizar manutenção preventiva;
- reutilizar equipamentos quando adequado;
- encaminhar resíduos eletrônicos para descarte correto;
- utilizar infraestrutura energeticamente eficiente.

---

# 15. Relação entre inventário de ativos e sustentabilidade

Um sistema de inventário de ativos pode contribuir para a sustentabilidade.

Ao conhecer os equipamentos existentes, a organização consegue acompanhar melhor:

- idade dos equipamentos;
- utilização;
- necessidade de substituição;
- manutenção;
- disponibilidade;
- descarte.

Isso pode reduzir compras desnecessárias e aumentar o aproveitamento da infraestrutura existente.

Portanto, a gestão adequada dos ativos não contribui apenas para a segurança da informação, mas também para uma utilização mais eficiente dos recursos tecnológicos.

---

# Conclusão

Uma aplicação Web depende de diversos conceitos além da programação.

A comunicação ocorre utilizando redes TCP/IP, sendo o TCP especialmente importante para aplicações Web que precisam de comunicação confiável.

Também é necessário implementar mecanismos de segurança, diferenciando autenticação e autorização e adotando princípios como menor privilégio e defesa em profundidade.

A proteção dos dados pessoais deve considerar os requisitos e princípios relacionados à LGPD, evitando coleta desnecessária e protegendo as informações armazenadas.

A estatística descritiva permite resumir informações do inventário e auxiliar na interpretação dos dados.

Por fim, sistemas computacionais possuem impacto ambiental, tornando importante considerar eficiência, utilização adequada dos equipamentos e descarte responsável.

Dessa forma, redes, segurança, privacidade, análise de dados e sustentabilidade devem ser consideradas em conjunto durante o desenvolvimento e operação de sistemas computacionais.