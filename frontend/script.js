"use strict";

const $ = (id) => document.getElementById(id);
const estado = { ativos: [], selecionado: null };
const labelsStatus = {
  ABERTO: "ABERTO · fera à solta",
  EM_TRATAMENTO: "EM TRATAMENTO · em caçada",
  CORRIGIDA: "CORRIGIDA · abatida",
  ACEITA: "ACEITA · monitorada"
};

function elemento(tag, texto, classe = "") {
  const item = document.createElement(tag);
  if (texto !== undefined && texto !== null) item.textContent = String(texto);
  if (classe) item.className = classe;
  return item;
}

function lerVulnerabilidades(ativo) {
  return Array.isArray(ativo.vulnerabilidades) ? ativo.vulnerabilidades : [];
}

function renderResumo() {
  const todas = estado.ativos.flatMap(lerVulnerabilidades);
  const contar = (status) => todas.filter(v => String(v.status || "").toUpperCase() === status).length;
  $("total-ativos").textContent = estado.ativos.length;
  $("total-abertas").textContent = contar("ABERTO");
  $("total-tratamento").textContent = contar("EM_TRATAMENTO");
  $("total-corrigidas").textContent = contar("CORRIGIDA");
}

function renderLista() {
  const termo = $("busca").value.toLocaleLowerCase("pt-BR").trim();
  const filtrados = estado.ativos.filter(a =>
    [a.id, a.nome, a.tipo, a.responsavel, a.setor]
      .some(campo => String(campo ?? "").toLocaleLowerCase("pt-BR").includes(termo))
  );

  if (!filtrados.some(a => String(a.id) === String(estado.selecionado))) {
    estado.selecionado = filtrados.length ? filtrados[0].id : null;
  }

  const corpo = $("lista-ativos");
  corpo.replaceChildren();
  for (const ativo of filtrados) {
    const linha = document.createElement("tr");
    if (String(ativo.id) === String(estado.selecionado)) linha.className = "selected";
    linha.appendChild(elemento("td", ativo.id));
    const celulaNome = document.createElement("td");
    const botao = elemento("button", ativo.nome || "Sem nome", "asset-button");
    botao.type = "button";
    botao.setAttribute("aria-label", `Inspecionar ${ativo.nome || "ativo"}`);
    botao.addEventListener("click", () => {
      estado.selecionado = ativo.id;
      renderLista();
    });
    celulaNome.appendChild(botao);
    linha.appendChild(celulaNome);
    linha.appendChild(elemento("td", ativo.tipo || "—", "asset-type"));
    linha.appendChild(elemento("td", ativo.responsavel || "—"));
    corpo.appendChild(linha);
  }

  $("mensagem").textContent = filtrados.length
    ? `${filtrados.length} ativo(s) exibido(s). Selecione um nome para inspecionar.`
    : "Nenhum ativo encontrado.";
  $("mensagem").classList.remove("error");
  renderDetalhe();
}

function renderDetalhe() {
  const container = $("detalhes");
  container.replaceChildren();
  const ativo = estado.ativos.find(a => String(a.id) === String(estado.selecionado));
  if (!ativo) {
    container.appendChild(elemento("p", "Nenhum ativo selecionado.", "placeholder"));
    return;
  }
  container.appendChild(elemento("h3", ativo.nome || "Ativo sem nome"));
  container.appendChild(elemento("p", `REGISTRO Nº ${ativo.id}`, "detail-id"));

  const detalhes = [
    ["Tipo", ativo.tipo],
    ["Responsável", ativo.responsavel],
    ["Setor", ativo.setor]
  ];
  const especificos = [
    ["Processador", ativo.processador],
    ["Serviço", ativo.servico],
    ["Endereço IP", ativo.endereco_ip],
    ["URL", ativo.url]
  ];
  for (const [rotulo, valor] of especificos) {
    if (valor !== null && valor !== undefined && valor !== "") detalhes.push([rotulo, valor]);
  }
  const grade = elemento("dl", null, "details-grid");
  for (const [chave, valor] of detalhes) {
    grade.appendChild(elemento("dt", chave));
    grade.appendChild(elemento("dd", valor || "—"));
  }
  container.appendChild(grade);
  container.appendChild(elemento("p", `Vulnerabilidades identificadas · ${lerVulnerabilidades(ativo).length}`, "section-title"));

  const vulnerabilidades = lerVulnerabilidades(ativo);
  if (!vulnerabilidades.length) {
    container.appendChild(elemento("p", "Nenhuma vulnerabilidade associada a este ativo.", "empty-vulns"));
    return;
  }

  const lista = elemento("ul", null, "vuln-list");
  for (const v of vulnerabilidades) {
    const item = elemento("li", null, "vuln-item");
    item.appendChild(elemento("div", v.descricao || "Vulnerabilidade sem descrição", "vuln-heading"));
    const meta = elemento("div", null, "vuln-meta");
    meta.appendChild(elemento("span", v.cve_id || v.categoria || "Sem referência"));
    meta.appendChild(elemento("span", `CVSS: ${v.severidade ?? "—"}`));
    const status = String(v.status || "").toUpperCase();
    meta.appendChild(elemento("span", labelsStatus[status] || status || "SEM STATUS", `status ${status.toLowerCase()}`));
    item.appendChild(meta);
    lista.appendChild(item);
  }
  container.appendChild(lista);
}

async function carregarAtivos() {
  $("atualizar").disabled = true;
  $("mensagem").textContent = "Buscando ativos na API...";
  $("mensagem").classList.remove("error");
  try {
    const resposta = await fetch("/ativos", { headers: { Accept: "application/json" }, cache: "no-store" });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    const dados = await resposta.json();
    if (!Array.isArray(dados)) throw new Error("Resposta inesperada da API");
    estado.ativos = dados;
    renderResumo();
    renderLista();
  } catch (erro) {
    $("mensagem").textContent = `Não foi possível consultar a API (${erro.message}).`;
    $("mensagem").classList.add("error");
  } finally {
    $("atualizar").disabled = false;
  }
}

$("busca").addEventListener("input", renderLista);
$("atualizar").addEventListener("click", carregarAtivos);
carregarAtivos();
