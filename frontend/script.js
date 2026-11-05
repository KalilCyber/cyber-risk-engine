"use strict";

/* Cyber Risk Engine: interface web. Os dados e regras vêm do backend FastAPI. */
const $ = id => document.getElementById(id);
const estado = { ativos: [], selecionado: null, tela: "ativos", cves: [], risco: null };
const tipos = { Notebook: "processador", Servidor: "servico", Roteador: "endereco_ip", AplicacaoWeb: "url" };
const rotulosEspecificos = { processador: "Processador", servico: "Serviço", endereco_ip: "Endereço IP", url: "URL" };
const estadosVuln = ["ABERTO", "EM_TRATAMENTO", "CORRIGIDA", "ACEITA"];
const niveis = ["MUITO_BAIXA", "BAIXA", "MODERADA", "ALTA", "MUITO_ALTA"];
const descricaoStatus = {
  ABERTO: "ABERTO · fera à solta",
  EM_TRATAMENTO: "EM TRATAMENTO · em caçada",
  CORRIGIDA: "CORRIGIDA · abatida",
  ACEITA: "ACEITA · monitorada"
};
const paginas = {
  ativos: ["OBSERVATÓRIO / INVENTÁRIO", "Vigília dos Ativos", "Gestão técnica dos ativos protegidos."],
  vulnerabilidades: ["INSPEÇÃO / FERAS", "Vulnerabilidades", "Identificação e tratamento das falhas de segurança."],
  dependencias: ["MAPA / VÍNCULOS", "Dependências", "Relações que propagam o risco entre ativos."],
  risco: ["CÁLCULO / ÁLGEBRA LINEAR", "Análise de risco", "Risco próprio e risco herdado das dependências."],
  nvd: ["PESQUISA / NVD", "Consulta CVE", "Vulnerabilidades publicadas, CVSS e referências."],
  guia: ["CÓDICE / ORIENTAÇÃO", "Como funciona", "Manual das ferramentas do Cyber Risk Engine."],
  diario: ["REGISTROS / CAÇADA", "Diário da Caçada", "Histórico de operações observadas pelo servidor."],
};

function el(tag, texto, classe = "") {
  const node = document.createElement(tag);
  if (texto !== null && texto !== undefined) node.textContent = String(texto);
  if (classe) node.className = classe;
  return node;
}
function td(texto, classe = "") { return el("td", texto, classe); }
function tr() { return document.createElement("tr"); }
function formatarNumero(v, digitos = 2) { return typeof v === "number" && Number.isFinite(v) ? v.toLocaleString("pt-BR", {maximumFractionDigits: digitos, minimumFractionDigits: 0}) : "—"; }
function vulnerabilidades(a) { return Array.isArray(a.vulnerabilidades) ? a.vulnerabilidades : []; }
function dependencias(a) { return Array.isArray(a.dependencias) ? a.dependencias : []; }
function ativoAtual() { return estado.ativos.find(a => String(a.id) === String(estado.selecionado)); }
function nomeAtivo(id) { const a = estado.ativos.find(x => x.id === id); return a ? `${a.nome} (ID ${id})` : `ID ${id}`; }
function informar(mensagem, erro = false) {
  const caixa = $("feedback"); caixa.textContent = mensagem; caixa.classList.toggle("error", erro);
}
function btn(texto, callback, classe = "text-button") {
  const b = el("button", texto, classe); b.type = "button"; b.addEventListener("click", callback); return b;
}
/* Leitura compacta das descrições da NVD, sem perder o texto completo. */
function descricaoExpansivel(texto, limite = 180) {
  const original = String(texto || "Descrição não informada.");
  if (original.length <= limite) return el("span", original);
  const caixa = el("div", null, "descricao-expansivel");
  const resumo = `${original.slice(0, limite).trimEnd()}…`;
  const conteudo = el("span", resumo);
  const alternar = btn("Ler descrição completa", () => {
    const expandido = alternar.getAttribute("aria-expanded") === "true";
    conteudo.textContent = expandido ? resumo : original;
    alternar.textContent = expandido ? "Recolher descrição" : "Ler descrição completa";
    alternar.setAttribute("aria-expanded", String(!expandido));
  }, "link-discreto");
  alternar.setAttribute("aria-expanded", "false");
  caixa.append(conteudo, alternar);
  return caixa;
}
function arrumarSelecionado() {
  if (!estado.ativos.some(a => a.id === estado.selecionado)) estado.selecionado = estado.ativos[0]?.id ?? null;
}
async function api(caminho, config = {}) {
  const options = {cache: "no-store", ...config, headers: { Accept: "application/json", ...(config.headers || {}) }};
  if (config.body && typeof config.body !== "string") {
    options.body = JSON.stringify(config.body);
    options.headers["Content-Type"] = "application/json";
  }
  let res;
  try { res = await fetch(caminho, options); }
  catch { throw new Error("Não foi possível conectar à API. Verifique se o FastAPI está executando."); }
  let data = null;
  try { data = await res.json(); } catch { /* respostas vazias */ }
  if (!res.ok) {
    let detail = data?.detail || `Erro HTTP ${res.status}`;
    if (Array.isArray(detail)) detail = detail.map(d => d.msg).join("; ");
    throw new Error(String(detail));
  }
  return data;
}

async function carregarAtivos(mostrarAviso = false) {
  const data = await api("/ativos");
  if (!Array.isArray(data)) throw new Error("A API retornou um inventário inválido.");
  estado.ativos = data;
  arrumarSelecionado();
  renderResumo(); renderAtivos(); atualizarSeletores(); renderVulnerabilidades(); renderDependencias();
  if (mostrarAviso) informar("Inventário sincronizado com a API.");
}
async function sincronizar() {
  const b = $("atualizar-geral"); b.disabled = true;
  try {
    await carregarAtivos(true);
    if (estado.tela === "risco") await carregarRisco();
  } catch (e) { informar(e.message, true); }
  finally { b.disabled = false; }
}
function abrirTela(tela) {
  estado.tela = tela;
  for (const b of document.querySelectorAll("[data-view]")) {
    const ativo = b.dataset.view === tela;
    b.classList.toggle("active", ativo);
    if (ativo) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current");
  }
  for (const [nome] of Object.entries(paginas)) {
    $("view-" + nome).hidden = nome !== tela;
    $("view-" + nome).classList.toggle("active", nome === tela);
  }
  const [eyebrow, titulo, subtitulo] = paginas[tela];
  $("secao-label").textContent = eyebrow;
  $("titulo-pagina").textContent = titulo;
  $("subtitulo-pagina").textContent = subtitulo;
  informar("");
  if (tela === "risco") carregarRisco();
  if (tela === "vulnerabilidades") renderVulnerabilidades();
  if (tela === "dependencias") renderDependencias();
  if (tela === "diario") carregarDiario();
}
function renderResumo() {
  const lista = estado.ativos.flatMap(vulnerabilidades);
  $("total-ativos").textContent = estado.ativos.length;
  for (const [id, status] of [["total-abertas", "ABERTO"], ["total-tratamento", "EM_TRATAMENTO"], ["total-corrigidas", "CORRIGIDA"]]) {
    $(id).textContent = lista.filter(v => v.status === status).length;
  }
}
function renderAtivos() {
  const termo = $("busca").value.toLocaleLowerCase("pt-BR").trim();
  const dados = estado.ativos.filter(a => [a.id, a.nome, a.tipo, a.responsavel, a.setor].some(v => String(v ?? "").toLocaleLowerCase("pt-BR").includes(termo)));
  const tbody = $("lista-ativos"); tbody.replaceChildren();
  for (const a of dados) {
    const linha = tr(); if (a.id === estado.selecionado) linha.classList.add("selected");
    linha.appendChild(td(a.id, "mono"));
    const celula = td(); celula.appendChild(btn(a.nome, () => { estado.selecionado = a.id; renderAtivos(); renderDetalhes(); }, "asset-button"));
    linha.appendChild(celula); linha.appendChild(td(a.tipo, "muted")); linha.appendChild(td(a.responsavel));
    tbody.appendChild(linha);
  }
  $("mensagem-ativos").textContent = dados.length ? `${dados.length} ativo(s) exibido(s). Selecione um nome para inspecionar.` : "Nenhum ativo encontrado.";
  renderDetalhes();
}
function renderDetalhes() {
  const caixa = $("detalhes"); caixa.replaceChildren(); const a = ativoAtual();
  if (!a) { caixa.appendChild(el("p", "Nenhum ativo selecionado.", "placeholder")); return; }
  caixa.appendChild(el("h3", a.nome));
  caixa.appendChild(el("p", `REGISTRO Nº ${a.id}`, "detail-id"));
  const botoes = el("div", null, "detail-actions");
  botoes.append(btn("Editar", () => formularioAtivo(a), "outline-btn small-btn"));
  botoes.append(btn("Excluir", () => excluirAtivo(a), "outline-btn small-btn"));
  botoes.append(btn("Vulnerabilidades", () => { abrirTela("vulnerabilidades"); $("filtro-vuln-ativo").value = String(a.id); renderVulnerabilidades(); }, "outline-btn small-btn"));
  botoes.append(btn("Dependências", () => { abrirTela("dependencias"); $("filtro-dep-ativo").value = String(a.id); renderDependencias(); }, "outline-btn small-btn"));
  caixa.appendChild(botoes);
  const dl = el("dl", null, "details-grid");
  for (const [nome, valor] of [["Tipo", a.tipo], ["Responsável", a.responsavel], ["Setor", a.setor], ...Object.entries(rotulosEspecificos).map(([chave, label]) => [label, a[chave]]).filter(([, v]) => v !== undefined && v !== null && v !== "")]) {
    dl.appendChild(el("dt", nome)); dl.appendChild(el("dd", valor || "—"));
  }
  caixa.appendChild(dl);
  caixa.appendChild(el("p", `Vulnerabilidades identificadas · ${vulnerabilidades(a).length}`, "section-title"));
  const vulnerab = vulnerabilidades(a);
  if (!vulnerab.length) { caixa.appendChild(el("p", "Nenhuma vulnerabilidade associada.", "empty-vulns")); return; }
  const ul = el("ul", null, "vuln-list");
  for (const v of vulnerab) {
    const li = el("li", null, "vuln-item"); const titulo = el("div", null, "vuln-heading"); titulo.appendChild(descricaoExpansivel(v.descricao)); li.appendChild(titulo);
    const meta = el("div", null, "vuln-meta");
    meta.append(el("span", v.cve_id || v.categoria || "Manual"), el("span", `CVSS: ${formatarNumero(v.severidade,1)}`));
    meta.appendChild(el("span", descricaoStatus[v.status] || v.status, `status ${String(v.status).toLowerCase()}`));
    li.appendChild(meta); ul.appendChild(li);
  }
  caixa.appendChild(ul);
}
function atualizarSeletores() {
  for (const id of ["filtro-vuln-ativo", "filtro-dep-ativo"]) {
    const select = $(id); const anterior = select.value; select.replaceChildren();
    for (const a of estado.ativos) { const o = el("option", `${a.nome} · ID ${a.id}`); o.value = String(a.id); select.appendChild(o); }
    select.value = estado.ativos.some(a => String(a.id) === anterior) ? anterior : String(estado.selecionado ?? "");
  }
}
function renderVulnerabilidades() {
  const id = Number($("filtro-vuln-ativo").value); const alvo = estado.ativos.find(a => a.id === id);
  const status = $("filtro-vuln-status").value;
  const lista = alvo ? vulnerabilidades(alvo).filter(v => !status || v.status === status) : [];
  const corpo = $("lista-vulns"); corpo.replaceChildren();
  for (const v of lista) {
    const linha = tr(); linha.append(td(v.id, "mono"), (() => { const c = td(); c.appendChild(descricaoExpansivel(v.descricao)); return c; })(), td([v.cve_id, v.cwe_id || v.categoria].filter(Boolean).join(" / ") || "—"), td(formatarNumero(v.severidade,1)));
    const st = td(); st.appendChild(el("span", descricaoStatus[v.status] || v.status, `status ${String(v.status).toLowerCase()}`)); linha.appendChild(st);
    const acoes = td(); const grupo = el("div", null, "row-actions");
    grupo.append(btn("Editar", () => formularioVulnerabilidade(alvo, v)));
    grupo.append(btn("Excluir", () => excluirVulnerabilidade(alvo, v), "text-button danger"));
    acoes.appendChild(grupo); linha.appendChild(acoes); corpo.appendChild(linha);
  }
  $("mensagem-vulns").textContent = alvo ? `${lista.length} vulnerabilidade(s) encontrada(s).` : "Cadastre um ativo para associar vulnerabilidades.";
  $("nova-vuln").disabled = !alvo;
}
function renderDependencias() {
  const id = Number($("filtro-dep-ativo").value); const alvo = estado.ativos.find(a => a.id === id);
  const tbody = $("lista-deps"); tbody.replaceChildren();
  for (const d of alvo ? dependencias(alvo) : []) {
    const linha = tr();
    linha.append(td(nomeAtivo(alvo.id)), td(nomeAtivo(d.id_ativo_origem)), td((d.nivel || "—").replaceAll("_", " ")), td(formatarNumero(Number(d.peso),2)));
    const acoes = td(); acoes.append(btn("Remover", () => excluirDependencia(alvo, d), "text-button danger"));
    linha.appendChild(acoes); tbody.appendChild(linha);
  }
  $("nova-dep").disabled = estado.ativos.length < 2;
  $("mensagem-deps").textContent = alvo ? `${dependencias(alvo).length} vínculo(s) de dependência.` : "Nenhum ativo disponível.";
}
async function carregarRisco() {
  const corpo = $("lista-riscos"); corpo.replaceChildren();
  $("risco-resumo").textContent = "Calculando o risco a partir das vulnerabilidades e dependências...";
  try {
    const dados = await api("/risco"); estado.risco = dados;
    const valores = dados.ativos.map(a => Math.max(0, Number(a.risco_efetivo) || 0));
    const max = Math.max(1, ...valores);
    for (const a of dados.ativos) {
      const linha = tr(); linha.append(td(`${a.nome} · ID ${a.id}`), td(formatarNumero(a.risco_proprio,4)), td(formatarNumero(a.risco_efetivo,4)));
      const graf = td(); const fundo = el("div", null, "risk-bar");
      const barra = document.createElement("span"); barra.style.width = `${Math.min(100, Math.max(0, 100 * a.risco_efetivo / max))}%`;
      fundo.appendChild(barra); graf.appendChild(fundo); linha.appendChild(graf); corpo.appendChild(linha);
    }
    $("risco-resumo").replaceChildren(el("span", `${dados.ativos.length} ativos analisados`), el("span", `Condição (I − A): ${formatarNumero(dados.numero_condicao,4)}`));
    $("matrizes").textContent = Object.entries(dados.matrizes).map(([nome, matriz]) => `${nome}:\n${JSON.stringify(matriz,null,2)}`).join("\n\n");
    if (!dados.ativos.length) $("risco-resumo").textContent = "Nenhum ativo cadastrado.";
  } catch (e) { $("risco-resumo").textContent = `Falha ao calcular risco: ${e.message}`; informar(e.message,true); }
}

/* Formulários em diálogo: campos gerados como elementos DOM (sem HTML não confiável). */
let salvarFormulario = null;
function campoInput(spec) {
  const wrapper = el("div", null, `field ${spec.wide ? "wide" : ""}`);
  const label = el("label", spec.label); label.htmlFor = `f-${spec.name}`; wrapper.appendChild(label);
  let controle;
  if (spec.type === "select") {
    controle = document.createElement("select");
    for (const op of spec.options || []) {
      const [valor, texto] = typeof op === "string" ? [op, op.replaceAll("_", " ")] : op;
      const option = el("option", texto); option.value = valor; controle.appendChild(option);
    }
  } else if (spec.type === "textarea") { controle = document.createElement("textarea"); }
  else { controle = document.createElement("input"); controle.type = spec.type || "text"; if (spec.min !== undefined) controle.min = spec.min; if (spec.max !== undefined) controle.max = spec.max; if (spec.step !== undefined) controle.step = spec.step; }
  controle.id = `f-${spec.name}`; controle.name = spec.name; controle.required = !!spec.required;
  if (spec.readonly) controle.readOnly = true;
  if (spec.placeholder) controle.placeholder = spec.placeholder;
  controle.value = spec.value === undefined || spec.value === null ? "" : String(spec.value);
  wrapper.appendChild(controle);
  return wrapper;
}
function modal(titulo, campos, onSave, extra = null) {
  const dlg = $("dialogo"); $("dialogo-titulo").textContent = titulo;
  $("dialogo-erro").textContent = "";
  const container = $("dialogo-campos"); container.replaceChildren(...campos.map(campoInput));
  salvarFormulario = onSave;
  if (extra) extra(container);
  dlg.showModal();
  const foco = container.querySelector("input:not([readonly]),textarea,select"); foco?.focus();
}
function dadosFormulario() {
  const obj = {};
  for (const [k,v] of new FormData($("form-dialogo")).entries()) {
    if (v !== "") obj[k] = v;
  }
  return obj;
}
function asNumber(dados, ...chaves) { for (const chave of chaves) if (dados[chave] !== undefined) dados[chave] = Number(dados[chave]); return dados; }
$("form-dialogo").addEventListener("submit", async event => {
  event.preventDefault(); const b = $("salvar-dialogo"); b.disabled = true; $("dialogo-erro").textContent = "";
  try {
    await salvarFormulario(dadosFormulario());
    $("dialogo").close();
    await carregarAtivos();
    if (estado.tela === "risco") await carregarRisco();
    informar("Alterações salvas com sucesso.");
  } catch(e) { $("dialogo-erro").textContent = e.message; }
  finally { b.disabled = false; }
});
$("cancelar-dialogo").addEventListener("click", () => $("dialogo").close());

function formularioAtivo(ativo = null) {
  const editando = !!ativo;
  const tipo = ativo?.tipo || "Notebook";
  const campos = [
    ...(!editando ? [
      {name:"id",label:"ID do ativo",type:"number",min:1,step:1,required:true},
      {name:"tipo",label:"Tipo do ativo",type:"select",options:Object.keys(tipos),value:tipo,required:true}
    ] : []),
    {name:"nome",label:"Nome / hostname",value:ativo?.nome,required:true,wide:true},
    {name:"responsavel",label:"Responsável",value:ativo?.responsavel,required:true},
    {name:"setor",label:"Setor",value:ativo?.setor,required:true},
    {name:editando?"atributo_especifico":"especifico",label:rotulosEspecificos[tipos[tipo]],value:ativo?.[tipos[tipo]],required:true,wide:true}
  ];
  modal(editando ? "Editar ativo" : "Cadastrar ativo", campos, async dados => {
    if (editando) await api(`/ativos/${ativo.id}`, {method:"PUT",body:dados});
    else {
      const campo = tipos[dados.tipo]; dados[campo] = dados.especifico; delete dados.especifico;
      asNumber(dados,"id"); const resposta = await api("/ativos", {method:"POST", body:dados}); estado.selecionado = resposta.id;
    }
  }, container => {
    if (editando) return;
    const select = container.querySelector('[name="tipo"]'); const especifico = container.querySelector('[name="especifico"]');
    select.addEventListener("change", () => { const campo = tipos[select.value]; especifico.parentElement.querySelector("label").textContent = rotulosEspecificos[campo]; especifico.value = ""; especifico.placeholder = campo === "endereco_ip" ? "192.168.0.10" : campo === "url" ? "https://exemplo.com" : ""; });
  });
}
async function excluirAtivo(ativo) {
  if (!confirm(`Excluir definitivamente ${ativo.nome} (ID ${ativo.id})? As vulnerabilidades associadas serão removidas do ativo.`)) return;
  try { await api(`/ativos/${ativo.id}`, {method:"DELETE"}); await carregarAtivos(); informar("Ativo removido."); }
  catch(e) { informar(e.message,true); }
}

function formularioVulnerabilidade(ativo = null, vuln = null, cve = null) {
  const alvo = ativo || estado.ativos.find(a => a.id === Number($("filtro-vuln-ativo").value)) || ativoAtual();
  if (!alvo) { informar("Cadastre um ativo antes.",true); return; }
  const editando = !!vuln;
  const idProximo = Math.max(0, ...estado.ativos.flatMap(a => vulnerabilidades(a).map(v => v.id))) + 1;
  const cvss = cve?.cvss || {};
  const campos = [
    ...(!editando ? [{name:"id",label:"ID da vulnerabilidade",type:"number",min:1,step:1,required:true,value:idProximo}] : []),
    {name:"status",label:"Tratamento",type:"select",options:estadosVuln,value:vuln?.status || "ABERTO",required:true},
    {name:"descricao",label:"Descrição",type:"textarea",value:vuln?.descricao || cve?.descricao || "",required:true,wide:true},
    {name:"categoria",label:"Categoria / CWE",value:vuln?.categoria || cve?.cwe_id || "CWE-NÃO-INFORMADA",required:true},
    {name:"severidade",label:"Severidade CVSS (0–10)",type:"number",min:0,max:10,step:"0.1",value:vuln?.severidade ?? cvss.score ?? 0,required:true},
    ...(!editando ? [
      {name:"cve_id",label:"CVE (opcional)",value:cve?.cve_id || ""},
      {name:"cwe_id",label:"CWE (opcional)",value:cve?.cwe_id || ""},
      {name:"cvss_version",label:"Versão CVSS",value:cvss.versao || ""},
      {name:"cvss_vector",label:"Vetor CVSS",value:cvss.vetor || "",wide:true}
    ] : [])
  ];
  modal(editando ? `Editar vulnerabilidade · ${vuln.id}` : `Associar vulnerabilidade · ${alvo.nome}`, campos, async dados => {
    asNumber(dados, "id", "severidade");
    if (editando) await api(`/ativos/${alvo.id}/vulnerabilidades/${vuln.id}`, {method:"PATCH",body:dados});
    else await api(`/ativos/${alvo.id}/vulnerabilidades`, {method:"POST",body:dados});
  });
}
async function excluirVulnerabilidade(ativo, vuln) {
  if (!confirm(`Remover a vulnerabilidade ID ${vuln.id} do ativo ${ativo.nome}?`)) return;
  try { await api(`/ativos/${ativo.id}/vulnerabilidades/${vuln.id}`, {method:"DELETE"}); await carregarAtivos(); informar("Vulnerabilidade removida."); }
  catch(e) { informar(e.message,true); }
}
function formularioDependencia() {
  const destino = estado.ativos.find(a => a.id === Number($("filtro-dep-ativo").value));
  if (!destino) return;
  const outras = estado.ativos.filter(a => a.id !== destino.id);
  if (!outras.length) { informar("Cadastre ao menos dois ativos.",true); return; }
  modal(`Novo vínculo · ${destino.nome}`, [
    {name:"origem_id",label:"Ativo de origem",type:"select",required:true,options:outras.map(a => [String(a.id),`${a.nome} · ID ${a.id}`])},
    {name:"nivel",label:"Nível da dependência",type:"select",required:true,options:niveis,value:"MODERADA"}
  ], async dados => { asNumber(dados,"origem_id"); await api(`/ativos/${destino.id}/dependencias`, {method:"POST",body:dados}); });
}
async function excluirDependencia(ativo, dependencia) {
  if (!confirm(`Remover a dependência de ${ativo.nome} em relação a ${nomeAtivo(dependencia.id_ativo_origem)}?`)) return;
  try { await api(`/ativos/${ativo.id}/dependencias/${dependencia.id_ativo_origem}`,{method:"DELETE"}); await carregarAtivos(); informar("Dependência removida."); }
  catch(e) { informar(e.message,true); }
}
async function pesquisarNVD(event) {
  event.preventDefault(); const termo = $("termo-nvd").value.trim();
  if (termo.length < 2) return;
  $("mensagem-nvd").textContent = "Consultando base NVD...";
  const tbody = $("lista-cves"); tbody.replaceChildren();
  try {
    const dados = await api(`/cves?termo=${encodeURIComponent(termo)}`);
    estado.cves = Array.isArray(dados) ? dados : [];
    for (const c of estado.cves) {
      const linha = tr(); linha.append(td(c.cve_id,"mono"), td((c.descricao || "").slice(0,240)), td(c.cwe_id || "—"), td(formatarNumero(c.cvss?.score,1)));
      const acoes = td(); acoes.append(btn("Associar", () => {
        if (!estado.ativos.length) { informar("Cadastre um ativo antes de associar CVEs.",true); return; }
        abrirTela("vulnerabilidades"); formularioVulnerabilidade(null, null, c);
      }, "outline-btn small-btn")); linha.appendChild(acoes); tbody.appendChild(linha);
    }
    $("mensagem-nvd").textContent = estado.cves.length ? `${estado.cves.length} resultado(s) encontrados.` : "Nenhum CVE encontrado para o termo e período pesquisados.";
  } catch(e) { $("mensagem-nvd").textContent = e.message; informar(e.message,true); }
}

/* O Diário vem do backend. Nunca fabricar eventos a partir de clicks locais. */
let eventosDiario = [];
const nomesEventosDiario = {
  ativo_cadastrado: "Ativo registrado",
  ativo_atualizado: "Ativo atualizado",
  ativo_removido: "Ativo removido",
  vulnerabilidade_associada: "Fera identificada · vulnerabilidade associada",
  vulnerabilidade_removida: "Vulnerabilidade removida",
  tratamento_atualizado: "Tratamento atualizado",
  dependencia_criada: "Vínculo criado",
  dependencia_removida: "Vínculo removido"
};
function formatarDataDiario(data) {
  const d = new Date(data);
  return Number.isNaN(d.getTime()) ? "Data indisponível" : d.toLocaleString("pt-BR", {dateStyle:"short", timeStyle:"medium"});
}
function renderDiario() {
  const filtro = $("filtro-diario").value;
  const visiveis = eventosDiario.filter(e => !filtro || e.tipo.includes(filtro));
  const lista = $("diario-eventos"); lista.replaceChildren();
  for (const e of visiveis) {
    const item = el("li", null, "diary-entry");
    const cabecalho = el("div", null, "diary-entry-head");
    cabecalho.append(el("strong", nomesEventosDiario[e.tipo] || e.tipo), el("time", formatarDataDiario(e.hora)));
    item.appendChild(cabecalho);
    const contexto = [e.ativo_nome ? `${e.ativo_nome} · ID ${e.ativo_id}` : (e.ativo_id !== undefined ? `Ativo ${e.ativo_id}` : ""), e.cve_id || (e.vulnerabilidade_id ? `Vulnerabilidade ${e.vulnerabilidade_id}` : "")].filter(Boolean).join(" / ");
    if (contexto) item.appendChild(el("p", contexto, "diary-context"));
    if (e.status_anterior !== undefined && e.status_novo !== undefined) {
      item.appendChild(el("p", `${e.status_anterior} → ${e.status_novo}`, "diary-change"));
    }
    if (e.origem_id !== undefined) item.appendChild(el("p", `Origem do vínculo: ativo ${e.origem_id}`, "diary-context"));
    lista.appendChild(item);
  }
  $("diario-mensagem").textContent = visiveis.length ? `${visiveis.length} evento(s) exibido(s), do mais recente ao mais antigo.` : "Nenhum registro corresponde ao filtro selecionado.";
}
async function carregarDiario() {
  $("diario-mensagem").textContent = "Consultando diário persistente...";
  try {
    const dados = await api("/diario?limite=200");
    eventosDiario = Array.isArray(dados.eventos) ? dados.eventos : [];
    $("diario-total").textContent = dados.total ?? 0;
    $("diario-tratamento").textContent = dados.resumo?.em_tratamento ?? 0;
    $("diario-corrigidas").textContent = dados.resumo?.corrigidas ?? 0;
    renderDiario();
  } catch(e) {
    $("diario-mensagem").textContent = `Não foi possível consultar o diário: ${e.message}`;
  }
}

/* Eventos */
document.querySelectorAll("[data-view]").forEach(b => b.addEventListener("click", () => abrirTela(b.dataset.view)));
$("atualizar-geral").addEventListener("click", sincronizar);
$("busca").addEventListener("input", renderAtivos);
$("novo-ativo").addEventListener("click", () => formularioAtivo());
$("filtro-vuln-ativo").addEventListener("change", renderVulnerabilidades);
$("filtro-vuln-status").addEventListener("change", renderVulnerabilidades);
$("nova-vuln").addEventListener("click", () => formularioVulnerabilidade());
$("filtro-dep-ativo").addEventListener("change", renderDependencias);
$("nova-dep").addEventListener("click", formularioDependencia);
$("recalcular").addEventListener("click", carregarRisco);
$("form-nvd").addEventListener("submit", pesquisarNVD);
$("filtro-diario").addEventListener("change", renderDiario);
$("recarregar-diario").addEventListener("click", carregarDiario);

carregarAtivos().catch(e => { informar(e.message,true); $("mensagem-ativos").textContent = "Não foi possível carregar os ativos."; });

const bgMusic = document.getElementById("bgMusic");
const toggleMusicBtn = document.getElementById("toggleMusicBtn");

let musicPlaying = false;

if (bgMusic) {
  bgMusic.volume = 0.25;
}

if (toggleMusicBtn && bgMusic) {
  toggleMusicBtn.addEventListener("click", async () => {
    try {
      if (!musicPlaying) {
        await bgMusic.play();
        musicPlaying = true;
        toggleMusicBtn.textContent = "Pausar trilha";
      } else {
        bgMusic.pause();
        musicPlaying = false;
        toggleMusicBtn.textContent = "Ativar trilha";
      }
    } catch (error) {
      console.error("Erro ao reproduzir música:", error);
      alert("O navegador bloqueou a reprodução automática. Clique novamente.");
    }
  });
}