// ==========================================
// DADOS SIMULADOS
// ==========================================

const ativos = [
    {
        id: 1,
        nome: "Notebook Financeiro",
        tipo: "Notebook",
        responsavel: "Ana",
        setor: "Financeiro",
        status: "Ativo",
        vulnerabilidades: 2
    },

    {
        id: 2,
        nome: "Servidor Principal",
        tipo: "Servidor",
        responsavel: "Carlos",
        setor: "TI",
        status: "Atenção",
        vulnerabilidades: 4
    },

    {
        id: 3,
        nome: "Roteador Matriz",
        tipo: "Roteador",
        responsavel: "Marcos",
        setor: "Infraestrutura",
        status: "Ativo",
        vulnerabilidades: 1
    },

    {
        id: 4,
        nome: "Portal Corporativo",
        tipo: "AplicacaoWeb",
        responsavel: "Juliana",
        setor: "Desenvolvimento",
        status: "Atenção",
        vulnerabilidades: 3
    },

    {
        id: 5,
        nome: "Notebook RH",
        tipo: "Notebook",
        responsavel: "Fernanda",
        setor: "Recursos Humanos",
        status: "Ativo",
        vulnerabilidades: 1
    },

    {
        id: 6,
        nome: "Servidor de Backup",
        tipo: "Servidor",
        responsavel: "Pedro",
        setor: "Infraestrutura",
        status: "Ativo",
        vulnerabilidades: 0
    }
];


// ==========================================
// ELEMENTOS DA PÁGINA
// ==========================================

const listaAtivos =
    document.getElementById("lista-ativos");

const campoBusca =
    document.getElementById("busca");

const filtroTipo =
    document.getElementById("filtro-tipo");

const totalAtivos =
    document.getElementById("total-ativos");

const totalVulnerabilidades =
    document.getElementById(
        "total-vulnerabilidades"
    );

const quantidadeExibida =
    document.getElementById(
        "quantidade-exibida"
    );

const secaoDetalhes =
    document.getElementById("detalhes");

const conteudoDetalhes =
    document.getElementById(
        "conteudo-detalhes"
    );


// ==========================================
// RESUMO DOS DADOS
// ==========================================

function atualizarResumo() {

    totalAtivos.textContent =
        ativos.length;

    const quantidadeVulnerabilidades =
        ativos
            .map(
                ativo =>
                    ativo.vulnerabilidades
            )
            .reduce(
                (total, quantidade) =>
                    total + quantidade,
                0
            );

    totalVulnerabilidades.textContent =
        quantidadeVulnerabilidades;
}


// ==========================================
// CRIAÇÃO DO HTML DOS CARDS
// ==========================================

function criarCardAtivo(ativo) {

    let classeStatus = "status-ativo";

    if (ativo.status === "Atenção") {
        classeStatus = "status-atencao";
    }


    return `
        <article class="ativo-card">

            <h3>
                ${ativo.nome}
            </h3>

            <p class="tipo">
                ${ativo.tipo}
            </p>

            <p>
                <strong>ID:</strong>
                ${ativo.id}
            </p>

            <p>
                <strong>Setor:</strong>
                ${ativo.setor}
            </p>

            <p>
                <strong>Responsável:</strong>
                ${ativo.responsavel}
            </p>

            <p>
                <strong>Vulnerabilidades:</strong>
                ${ativo.vulnerabilidades}
            </p>

            <p
                class="
                    status
                    ${classeStatus}
                "
            >
                ${ativo.status}
            </p>

            <button
                class="botao-detalhes"
                onclick="
                    exibirDetalhes(${ativo.id})
                "
            >
                Ver detalhes
            </button>

        </article>
    `;
}


// ==========================================
// RENDERIZAÇÃO DA LISTA
// ==========================================

function renderizarAtivos(lista) {

    quantidadeExibida.textContent =
        `${lista.length} ativo(s) encontrado(s)`;


    if (lista.length === 0) {

        listaAtivos.innerHTML = `
            <div class="sem-resultados">
                Nenhum ativo encontrado.
            </div>
        `;

        return;
    }


    listaAtivos.innerHTML =
        lista
            .map(criarCardAtivo)
            .join("");
}


// ==========================================
// FILTRO
// ==========================================

function filtrarAtivos() {

    const textoBusca =
        campoBusca.value
            .toLowerCase()
            .trim();

    const tipoSelecionado =
        filtroTipo.value;


    const resultado =
        ativos.filter(
            ativo => {

                const correspondeNome =
                    ativo.nome
                        .toLowerCase()
                        .includes(textoBusca);


                const correspondeTipo =
                    tipoSelecionado === "todos"
                    ||
                    ativo.tipo === tipoSelecionado;


                return (
                    correspondeNome
                    &&
                    correspondeTipo
                );
            }
        );


    renderizarAtivos(resultado);
}


// ==========================================
// DETALHES DE UM ATIVO
// ==========================================

function exibirDetalhes(id) {

    const ativo =
        ativos.find(
            ativo => ativo.id === id
        );


    if (!ativo) {
        return;
    }


    conteudoDetalhes.innerHTML = `
        <p>
            <strong>ID:</strong>
            ${ativo.id}
        </p>

        <p>
            <strong>Nome:</strong>
            ${ativo.nome}
        </p>

        <p>
            <strong>Tipo:</strong>
            ${ativo.tipo}
        </p>

        <p>
            <strong>Responsável:</strong>
            ${ativo.responsavel}
        </p>

        <p>
            <strong>Setor:</strong>
            ${ativo.setor}
        </p>

        <p>
            <strong>Status:</strong>
            ${ativo.status}
        </p>

        <p>
            <strong>Vulnerabilidades:</strong>
            ${ativo.vulnerabilidades}
        </p>
    `;


    secaoDetalhes.classList.remove(
        "oculto"
    );


    secaoDetalhes.scrollIntoView({
        behavior: "smooth"
    });
}


// ==========================================
// EVENTOS
// ==========================================

campoBusca.addEventListener(
    "input",
    filtrarAtivos
);


filtroTipo.addEventListener(
    "change",
    filtrarAtivos
);


// ==========================================
// INICIALIZAÇÃO
// ==========================================

atualizarResumo();

renderizarAtivos(ativos);