"""
Pizzaria do Hacker - API
Versao SEGURA (Missao 2). Na Missao 4 vamos "estragar" de proposito
para ver os gates de SAST e SCA barrarem o deploy.
"""
import sqlite3
import threading
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Pizzaria do Hacker", docs_url=None, redoc_url=None)  # docs desligadas em "producao"

# Banco em memoria: nada e gravado em disco (combina com readOnlyRootFilesystem)
_db = sqlite3.connect(":memory:", check_same_thread=False)
_db.row_factory = sqlite3.Row
_lock = threading.Lock()

CARDAPIO = [
    ("Margherita SQL", "Molho de tomate, mussarela e manjericao. Sem injecao, prometemos.", 9.50, "🍅"),
    ("Pepperoni Overflow", "Tanto pepperoni que estoura o buffer da massa.", 11.90, "🔥"),
    ("Quatro Queijos XSS", "Quatro queijos devidamente escapados.", 12.50, "🧀"),
    ("Calabresa Zero-Day", "Ninguem conhecia esta receita ate hoje.", 10.90, "🌶️"),
    ("Frango Root", "Frango com catupiry e privilegios minimos.", 11.50, "🐔"),
    ("Portuguesa Least Privilege", "So os ingredientes estritamente necessarios.", 10.50, "🥚"),
]

with _lock:
    _db.execute(
        "CREATE TABLE pizzas (id INTEGER PRIMARY KEY, nome TEXT, descricao TEXT, preco REAL, emoji TEXT)"
    )
    _db.execute(
        "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, pizza_id INTEGER, quantidade INTEGER, "
        "cliente TEXT, criado_em TEXT)"
    )
    _db.executemany("INSERT INTO pizzas (nome, descricao, preco, emoji) VALUES (?, ?, ?, ?)", CARDAPIO)
    _db.commit()


class Pedido(BaseModel):
    pizza_id: int = Field(gt=0)
    quantidade: int = Field(gt=0, le=20)
    cliente: str = Field(min_length=1, max_length=40)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/menu")
def menu(busca: str = Query(default="", max_length=50)):
    # Query PARAMETRIZADA: o texto do usuario nunca vira codigo SQL
    with _lock:
        rows = _db.execute(
            "SELECT id, nome, descricao, preco, emoji FROM pizzas WHERE nome LIKE ? ORDER BY id",
            (f"%{busca}%",),
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/pedidos", status_code=201)
def criar_pedido(p: Pedido):
    with _lock:
        pizza = _db.execute("SELECT nome FROM pizzas WHERE id = ?", (p.pizza_id,)).fetchone()
        if not pizza:
            raise HTTPException(status_code=404, detail="Pizza nao encontrada")
        cur = _db.execute(
            "INSERT INTO pedidos (pizza_id, quantidade, cliente, criado_em) VALUES (?, ?, ?, ?)",
            (p.pizza_id, p.quantidade, p.cliente, datetime.now(timezone.utc).isoformat()),
        )
        _db.commit()
    return {"pedido_id": cur.lastrowid, "pizza": pizza["nome"], "quantidade": p.quantidade,
            "mensagem": f"Pedido confirmado, {p.cliente}! Sua pizza esta no forno. 🍕"}
