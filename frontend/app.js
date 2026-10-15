// Versao SEGURA: todo texto vindo da API entra com textContent (nunca innerHTML),
// entao um nome de pizza malicioso nao vira codigo no navegador (anti-XSS).

const cardapio = document.getElementById("cardapio");
const select = document.getElementById("pizza");
const busca = document.getElementById("busca");
const resultado = document.getElementById("resultado");

function el(tag, classe, texto) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto !== undefined) e.textContent = texto;
  return e;
}

async function carregarMenu(termo = "") {
  const resp = await fetch(`/api/menu?busca=${encodeURIComponent(termo)}`);
  const pizzas = await resp.json();

  cardapio.replaceChildren();
  if (pizzas.length === 0) {
    cardapio.append(el("p", "vazio", "Nenhuma pizza encontrada. 🕵️"));
  }
  for (const p of pizzas) {
    const card = el("article", "card");
    card.append(
      el("div", "emoji", p.emoji),
      el("h3", null, p.nome),
      el("p", "desc", p.descricao),
      el("p", "preco", `€ ${p.preco.toFixed(2)}`)
    );
    cardapio.append(card);
  }

  if (termo === "") {
    select.replaceChildren(...pizzas.map(p => {
      const o = el("option", null, p.nome);
      o.value = p.id;
      return o;
    }));
  }
}

let timer;
busca.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(() => carregarMenu(busca.value), 250);
});

document.getElementById("form-pedido").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const body = {
    cliente: document.getElementById("cliente").value,
    pizza_id: Number(select.value),
    quantidade: Number(document.getElementById("quantidade").value),
  };
  const resp = await fetch("/api/pedidos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const dados = await resp.json();
  resultado.textContent = resp.ok
    ? `#${dados.pedido_id} — ${dados.mensagem}`
    : "Ops, pedido inválido. 🚫";
});

carregarMenu();
