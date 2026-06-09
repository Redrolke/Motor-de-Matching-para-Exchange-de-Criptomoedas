"""
order_book.py
=============
Motor de Matching (Order Book) para Exchange de Criptomoedas.

Utiliza exclusivamente as estruturas implementadas em structures.py:
  - MaxHeap      → buy orders  (RF01)
  - MinHeap      → sell orders (RF01)
  - BST          → histórico de transações (RF02)
  - HashTable    → saldos das contas (RF03)

Complexidade do matching: O(log N) por operação de heap.
"""

from structures import MaxHeap, MinHeap, BST, HashTable


class OrderBook:
    """
    Motor principal de matching.

    Fluxo:
      1. process_order(order) → classifica como BUY ou SELL
      2. Tenta cruzar com o topo oposto da heap
      3. Se match: executa trade, registra na BST, atualiza saldos na HashTable
      4. Se sem match ou parcial: mantém o saldo da ordem na heap
    """

    def __init__(self):
        self.buy_heap    = MaxHeap()       # RF01 — Max-Heap
        self.sell_heap   = MinHeap()       # RF01 — Min-Heap
        self.tx_tree     = BST()           # RF02 — BST histórico
        self.balances    = HashTable()     # RF03 — saldos
        self.transactions: list[dict] = []

        self._tx_counter = 0

    # ─────────────────────────────────────────────────────────────────────────
    # BALANCES (RF03)
    # ─────────────────────────────────────────────────────────────────────────
    def _get_balance(self, account_id: str) -> dict:
        bal = self.balances.get(account_id)
        if bal is None:
            bal = {"BTC": 0.0, "USD": 0.0}
            self.balances.set(account_id, bal)
        return bal

    def _credit(self, account_id: str, asset: str, amount: float):
        bal = self._get_balance(account_id)
        bal[asset] = round(bal[asset] + amount, 8)
        self.balances.set(account_id, bal)

    def _debit(self, account_id: str, asset: str, amount: float):
        bal = self._get_balance(account_id)
        bal[asset] = round(bal[asset] - amount, 8)
        self.balances.set(account_id, bal)

    # ─────────────────────────────────────────────────────────────────────────
    # MATCHING ENGINE
    # ─────────────────────────────────────────────────────────────────────────
    def process_order(self, order: dict):
        """
        Processa uma ordem de compra ou venda.
        Parâmetros esperados no dict:
          order_id    : str
          account_id  : str
          side        : "buy" | "sell"
          price       : float
          quantity    : float   (BTC)
          timestamp   : int
        """
        side = order["side"]
        if side == "buy":
            self._match_buy(order)
        else:
            self._match_sell(order)

    def _match_buy(self, buy_order: dict):
        """Tenta cruzar compra com a venda mais barata disponível."""
        qty_remaining = buy_order["quantity"]

        while qty_remaining > 1e-8 and not self.sell_heap.is_empty():
            best_sell = self.sell_heap.peek()

            # Condição de cruzamento: preço de compra >= preço de venda
            if buy_order["price"] < best_sell["price"]:
                break

            self.sell_heap.extract_min()
            traded_qty   = min(qty_remaining, best_sell["quantity"])
            traded_price = best_sell["price"]   # preço da ordem passiva

            self._execute_trade(
                buyer_id    = buy_order["account_id"],
                seller_id   = best_sell["account_id"],
                price       = traded_price,
                quantity    = traded_qty,
                buy_order_id  = buy_order["order_id"],
                sell_order_id = best_sell["order_id"],
                timestamp   = max(buy_order["timestamp"], best_sell["timestamp"])
            )

            qty_remaining = round(qty_remaining - traded_qty, 8)

            # Reinsere saldo da venda, se houver
            leftover_sell = round(best_sell["quantity"] - traded_qty, 8)
            if leftover_sell > 1e-8:
                remainder = dict(best_sell)
                remainder["quantity"] = leftover_sell
                self.sell_heap.insert(remainder)

        # Saldo de compra não executado entra no book
        if qty_remaining > 1e-8:
            remaining_order = dict(buy_order)
            remaining_order["quantity"] = qty_remaining
            self.buy_heap.insert(remaining_order)

    def _match_sell(self, sell_order: dict):
        """Tenta cruzar venda com a compra mais cara disponível."""
        qty_remaining = sell_order["quantity"]

        while qty_remaining > 1e-8 and not self.buy_heap.is_empty():
            best_buy = self.buy_heap.peek()

            if sell_order["price"] > best_buy["price"]:
                break

            self.buy_heap.extract_max()
            traded_qty   = min(qty_remaining, best_buy["quantity"])
            traded_price = best_buy["price"]

            self._execute_trade(
                buyer_id    = best_buy["account_id"],
                seller_id   = sell_order["account_id"],
                price       = traded_price,
                quantity    = traded_qty,
                buy_order_id  = best_buy["order_id"],
                sell_order_id = sell_order["order_id"],
                timestamp   = max(sell_order["timestamp"], best_buy["timestamp"])
            )

            qty_remaining = round(qty_remaining - traded_qty, 8)

            leftover_buy = round(best_buy["quantity"] - traded_qty, 8)
            if leftover_buy > 1e-8:
                remainder = dict(best_buy)
                remainder["quantity"] = leftover_buy
                self.buy_heap.insert(remainder)

        if qty_remaining > 1e-8:
            remaining_order = dict(sell_order)
            remaining_order["quantity"] = qty_remaining
            self.sell_heap.insert(remaining_order)

    # ─────────────────────────────────────────────────────────────────────────
    # EXECUTE TRADE
    # ─────────────────────────────────────────────────────────────────────────
    def _execute_trade(self, buyer_id, seller_id, price,
                       quantity, buy_order_id, sell_order_id, timestamp):
        self._tx_counter += 1
        tx_id = f"TX{self._tx_counter:08d}"

        usd_amount = round(price * quantity, 8)

        # Atualiza saldos (RF03 — O(1))
        self._debit (seller_id, "BTC", quantity)
        self._credit(buyer_id,  "BTC", quantity)
        self._debit (buyer_id,  "USD", usd_amount)
        self._credit(seller_id, "USD", usd_amount)

        tx = {
            "transaction_id"  : tx_id,
            "buy_order_id"    : buy_order_id,
            "sell_order_id"   : sell_order_id,
            "buyer_account"   : buyer_id,
            "seller_account"  : seller_id,
            "price"           : price,
            "quantity"        : quantity,
            "total_usd"       : usd_amount,
            "timestamp"       : timestamp,
        }

        # Armazena no BST (RF02 — O(log N))
        self.tx_tree.insert(tx_id, tx)
        self.transactions.append(tx)

    # ─────────────────────────────────────────────────────────────────────────
    # SNAPSHOTS
    # ─────────────────────────────────────────────────────────────────────────
    def snapshot_balances(self) -> dict:
        """Retorna todos os saldos como dict serializável."""
        return {k: v for k, v in self.balances.items()}

    def snapshot_order_book(self) -> dict:
        """Retorna o estado das heaps (cópias — não altera estrutura)."""
        return {
            "buy_orders" : [dict(o) for o in self.buy_heap._data],
            "sell_orders": [dict(o) for o in self.sell_heap._data],
        }

    def search_transaction(self, tx_id: str) -> dict:
        """Busca no BST. O(log N) esperado."""
        return self.tx_tree.search(tx_id)
