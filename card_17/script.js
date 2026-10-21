const API_URL =
    "https://jsonplaceholder.typicode.com/users";


const botaoCarregar =
    document.getElementById(
        "botao-carregar"
    );


const listaDados =
    document.getElementById(
        "lista-dados"
    );


const mensagem =
    document.getElementById(
        "mensagem"
    );


// ==========================================
// FUNÇÃO ASSÍNCRONA
// ==========================================

async function carregarUsuarios() {

    mensagem.textContent =
        "Carregando dados...";

    mensagem.className =
        "mensagem";

    listaDados.innerHTML = "";

    botaoCarregar.disabled = true;


    try {

        // Requisição HTTP utilizando Fetch API
        const resposta =
            await fetch(API_URL);


        // Verifica se a resposta HTTP foi bem-sucedida
        if (!resposta.ok) {

            throw new Error(
                `Erro HTTP: ${resposta.status}`
            );

        }


        // Converte a resposta JSON
        // em objetos JavaScript
        const usuarios =
            await resposta.json();


        renderizarUsuarios(
            usuarios
        );


        mensagem.textContent =
            `${usuarios.length} usuário(s) carregado(s) com sucesso.`;

        mensagem.className =
            "mensagem sucesso";

    }

    catch (erro) {

        console.error(
            "Erro ao carregar dados:",
            erro
        );


        mensagem.textContent =
            "Não foi possível carregar os dados da API.";

        mensagem.className =
            "mensagem erro";

    }

    finally {

        botaoCarregar.disabled =
            false;

    }

}


// ==========================================
// RENDERIZAÇÃO
// ==========================================

function renderizarUsuarios(
    usuarios
) {

    listaDados.innerHTML =
        usuarios
            .map(
                usuario => `
                    <article class="usuario-card">

                        <h2>
                            ${usuario.name}
                        </h2>

                        <p>
                            <strong>ID:</strong>
                            ${usuario.id}
                        </p>

                        <p>
                            <strong>Usuário:</strong>
                            ${usuario.username}
                        </p>

                        <p>
                            <strong>E-mail:</strong>
                            ${usuario.email}
                        </p>

                        <p>
                            <strong>Telefone:</strong>
                            ${usuario.phone}
                        </p>

                        <p>
                            <strong>Empresa:</strong>
                            ${usuario.company.name}
                        </p>

                    </article>
                `
            )
            .join("");

}


// ==========================================
// EVENTO DO BOTÃO
// ==========================================

botaoCarregar.addEventListener(
    "click",
    carregarUsuarios
);