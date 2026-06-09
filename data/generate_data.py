"""
generate_data.py
================
Gerador dos três níveis de teste: básico, avançado e estresse.
Usa apenas: random, uuid, json, time  (bibliotecas permitidas para geração).

Uso:
  python data/generate_data.py
  → Cria data/input_basico.json, data/input_avancado.json, data/input_estresse.json
"""

import json
import random
import uuid
import time
import os

SEED = 42
random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__))


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def make_order(side: str, price: float, quantity: float,
               account_id: str, ts: int) -> dict:
    return {
        "order_id"  : str(uuid.uuid4()),
        "account_id": account_id,
        "side"      : side,
        "price"     : round(price, 2),
        "quantity"  : round(quantity, 8),
        "timestamp" : ts,
    }


def initial_balances(accounts: list[str],
                     btc_range=(0, 10),
                     usd_range=(0, 100_000)) -> dict:
    return {
        acc: {
            "BTC": round(random.uniform(*btc_range), 8),
            "USD": round(random.uniform(*usd_range), 2),
        }
        for acc in accounts
    }


def save(obj: dict, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    size_kb = os.path.getsize(path) / 1024
    print(f"  ✓ {filename:35s} ({len(obj['orders']):>7,} ordens | {size_kb:,.1f} KB)")


# ─────────────────────────────────────────────────────────────────────────────
# BÁSICO — valida lógica central
# ─────────────────────────────────────────────────────────────────────────────
def generate_basic() -> dict:
    """
    20 ordens simples — preços alinhados para garantir vários matches.
    5 contas, saldos generosos para evitar negativos.
    """
    accounts = [f"ACC_{i:03d}" for i in range(1, 6)]
    orders   = []
    ts       = int(time.time()) * 1000

    # 10 vendas (preços 49.000 a 50.000)
    for i in range(10):
        price = 49_000 + i * 100
        qty   = round(random.uniform(0.01, 0.5), 8)
        acc   = random.choice(accounts)
        orders.append(make_order("sell", price, qty, acc, ts + i))

    # 10 compras (preços 49.500 a 50.500) → alguns devem cruzar
    for i in range(10):
        price = 49_500 + i * 100
        qty   = round(random.uniform(0.01, 0.5), 8)
        acc   = random.choice(accounts)
        orders.append(make_order("buy", price, qty, acc, ts + 10 + i))

    random.shuffle(orders)

    return {
        "metadata": {"level": "basico", "description": "Validação lógica central"},
        "initial_balances": initial_balances(accounts, btc_range=(5, 10), usd_range=(500_000, 1_000_000)),
        "orders": orders,
    }


# ─────────────────────────────────────────────────────────────────────────────
# AVANÇADO — edge cases
# ─────────────────────────────────────────────────────────────────────────────
def generate_advanced() -> dict:
    """
    1.000 ordens com edge cases:
      - preços iguais (múltiplos matches simultâneos)
      - quantidades muito pequenas (1 satoshi = 0.00000001 BTC)
      - contas com saldo zero
      - ordens sem match (preço incompatível)
      - ordens duplicadas de mesma conta
      - ciclos de compra/venda entre mesmas contas
      - contas desconectadas (nunca cruzam)
    """
    accounts = [f"ACC_{i:03d}" for i in range(1, 21)]
    orders   = []
    ts       = int(time.time()) * 1000

    # — Bloco 1: matches normais (400 ordens) ——————————————————————————────
    for i in range(200):
        price = round(random.uniform(49_000, 51_000), 2)
        qty   = round(random.uniform(0.001, 1.0), 8)
        acc   = random.choice(accounts)
        orders.append(make_order("sell", price, qty, acc, ts + i))
        orders.append(make_order("buy",  price + random.uniform(-200, 200), qty, acc, ts + i + 1))

    # — Bloco 2: preços iguais (colisão de heap) ———————————————————————————
    for _ in range(100):
        price = 50_000.00
        for side in ["buy", "sell"] * 2:
            qty = round(random.uniform(0.01, 0.1), 8)
            acc = random.choice(accounts)
            orders.append(make_order(side, price, qty, acc, ts + 5000 + _))

    # — Bloco 3: micro-quantidades ————————————————————————————————————————
    for i in range(50):
        orders.append(make_order("sell", 50_000, 0.00000001, accounts[0], ts + 6000 + i))
        orders.append(make_order("buy",  50_000, 0.00000001, accounts[1], ts + 6001 + i))

    # — Bloco 4: ordens sem match (spread muito grande) ————————————————————
    for i in range(100):
        orders.append(make_order("buy",  30_000, 0.1, random.choice(accounts), ts + 7000 + i))
        orders.append(make_order("sell", 70_000, 0.1, random.choice(accounts), ts + 7001 + i))

    # — Bloco 5: contas isoladas (nunca cruzam entre si) ———————————————————
    isolated = ["ISO_001", "ISO_002"]
    for i in range(50):
        orders.append(make_order("buy",  40_000, 0.5, isolated[0], ts + 9000 + i))
        orders.append(make_order("sell", 60_000, 0.5, isolated[1], ts + 9001 + i))

    random.shuffle(orders)

    balances = initial_balances(accounts, btc_range=(10, 50), usd_range=(1_000_000, 5_000_000))
    balances["ISO_001"] = {"BTC": 0.0,  "USD": 2_000_000.0}
    balances["ISO_002"] = {"BTC": 100.0, "USD": 0.0}

    return {
        "metadata": {
            "level": "avancado",
            "description": "Edge cases: preços iguais, micro-quantidades, contas isoladas, sem match",
        },
        "initial_balances": balances,
        "orders": orders,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ESTRESSE — 100.000 ordens intercaladas
# ─────────────────────────────────────────────────────────────────────────────
def generate_stress() -> dict:
    """
    100.000 ordens intercaladas de compra/venda.
    Força:
      - colisões constantes no Order Book
      - reorganizações frequentes das Heaps (sift_up / sift_down)
      - alto volume de transações no BST e na HashTable
    """
    n_orders  = 100_000
    n_accounts = 500
    accounts  = [f"ACC_{i:05d}" for i in range(n_accounts)]
    orders    = []

    # Simula preço de mercado com random walk para criar crossing natural
    price = 50_000.0
    ts    = int(time.time()) * 1000

    for i in range(n_orders):
        # Random walk no preço de mercado (±0,5%)
        price = max(1_000, price * (1 + random.uniform(-0.005, 0.005)))

        # Alterna compra/venda com leve spread variável
        if i % 2 == 0:
            side  = "buy"
            limit = round(price * random.uniform(0.995, 1.010), 2)
        else:
            side  = "sell"
            limit = round(price * random.uniform(0.990, 1.005), 2)

        qty = round(random.uniform(0.001, 2.0), 8)
        acc = accounts[i % n_accounts]
        orders.append(make_order(side, limit, qty, acc, ts + i))

    # NÃO embaralhamos — a intercalação já é natural pelo alternância acima
    # (embaralhar quebraria a sequência temporal, mas é permitido)
    # random.shuffle(orders)  ← comentado intencionalmente para refletir stream real

    return {
        "metadata": {
            "level"      : "estresse",
            "description": "100.000 ordens intercaladas com random walk de preço",
            "n_orders"   : n_orders,
            "n_accounts" : n_accounts,
        },
        "initial_balances": initial_balances(
            accounts, btc_range=(50, 500), usd_range=(5_000_000, 50_000_000)
        ),
        "orders": orders,
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Gerando arquivos de teste...\n")

    save(generate_basic(),    "input_basico.json")
    save(generate_advanced(), "input_avancado.json")

    print("\n  [!] Gerando estresse (100.000 ordens) — pode demorar alguns segundos...")
    save(generate_stress(),   "input_estresse.json")

    print("\nConcluído. Execute:")
    print("  python src/main.py --input data/input_basico.json   --output data/output_basico.json   --verbose")
    print("  python src/main.py --input data/input_avancado.json --output data/output_avancado.json --verbose")
    print("  python src/main.py --input data/input_estresse.json --output data/output_estresse.json --verbose")
