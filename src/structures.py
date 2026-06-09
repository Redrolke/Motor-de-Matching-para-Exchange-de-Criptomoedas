class MaxHeap:
 
    def __init__(self):
        self._data = []

    @staticmethod
    def _parent(i):   return (i - 1) // 2
    @staticmethod
    def _left(i):     return 2 * i + 1
    @staticmethod
    def _right(i):    return 2 * i + 2

    def _compare(self, a, b):
        pa, ta = self._data[a]["price"], self._data[a]["timestamp"]
        pb, tb = self._data[b]["price"], self._data[b]["timestamp"]
        if pa != pb:
            return pa > pb 
        return ta < tb             

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i):
        while i > 0:
            p = self._parent(i)
            if self._compare(i, p):
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            largest = i
            l, r = self._left(i), self._right(i)
            if l < n and self._compare(l, largest):
                largest = l
            if r < n and self._compare(r, largest):
                largest = r
            if largest == i:
                break
            self._swap(i, largest)
            i = largest


    def insert(self, order: dict):
        self._data.append(order)
        self._sift_up(len(self._data) - 1)

    def extract_max(self) -> dict:
        if not self._data:
            return None
        self._swap(0, len(self._data) - 1)
        top = self._data.pop()
        if self._data:
            self._sift_down(0)
        return top

    def peek(self) -> dict:
        return self._data[0] if self._data else None

    def __len__(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0


class MinHeap:

    def __init__(self):
        self._data = []

    @staticmethod
    def _parent(i):   return (i - 1) // 2
    @staticmethod
    def _left(i):     return 2 * i + 1
    @staticmethod
    def _right(i):    return 2 * i + 2

    def _compare(self, a, b):
        pa, ta = self._data[a]["price"], self._data[a]["timestamp"]
        pb, tb = self._data[b]["price"], self._data[b]["timestamp"]
        if pa != pb:
            return pa < pb          # menor preço tem prioridade
        return ta < tb              # empate: chegou primeiro

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i):
        while i > 0:
            p = self._parent(i)
            if self._compare(i, p):
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            smallest = i
            l, r = self._left(i), self._right(i)
            if l < n and self._compare(l, smallest):
                smallest = l
            if r < n and self._compare(r, smallest):
                smallest = r
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def insert(self, order: dict):
        """O(log N)"""
        self._data.append(order)
        self._sift_up(len(self._data) - 1)

    def extract_min(self) -> dict:
        """Remove e retorna a ordem de venda com menor preço. O(log N)"""
        if not self._data:
            return None
        self._swap(0, len(self._data) - 1)
        top = self._data.pop()
        if self._data:
            self._sift_down(0)
        return top

    def peek(self) -> dict:
        return self._data[0] if self._data else None

    def __len__(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0


# ─────────────────────────────────────────────────────────────────────────────
# BST  (Transaction History)
# ─────────────────────────────────────────────────────────────────────────────
class _AVLNode:
    """Nó de AVL Tree com fator de altura para balanceamento automático."""
    __slots__ = ("key", "value", "left", "right", "height")

    def __init__(self, key, value):
        self.key    = key
        self.value  = value
        self.left   = None
        self.right  = None
        self.height = 1


class BST:
    """
    Árvore AVL (AVL Tree) — BST auto-balanceada.
    Garante altura O(log N) mesmo para chaves sequenciais.
    Chave: transaction_id (string).

    Invariante AVL: |altura(esq) - altura(dir)| <= 1 para todo nó.
    Rotações: LL, RR, LR, RL — executadas automaticamente no insert.

    Complexidade garantida:
      insert  O(log N)
      search  O(log N)
      height  O(log N)
    """

    def __init__(self):
        self._root = None
        self._size = 0

    # ── altura ────────────────────────────────────────────────────────────────
    @staticmethod
    def _h(node) -> int:
        return node.height if node else 0

    def _update_height(self, node):
        node.height = 1 + max(self._h(node.left), self._h(node.right))

    def _balance_factor(self, node) -> int:
        return self._h(node.left) - self._h(node.right)

    # ── rotações ──────────────────────────────────────────────────────────────
    def _rotate_right(self, y):
        x  = y.left
        T2 = x.right
        x.right = y
        y.left  = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        y  = x.right
        T2 = y.left
        y.left  = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node):
        self._update_height(node)
        bf = self._balance_factor(node)

        # LL
        if bf > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)
        # LR
        if bf > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # RR
        if bf < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)
        # RL
        if bf < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    # ── insert recursivo (profundidade máxima O(log N) — seguro) ─────────────
    def _insert(self, node, key, value):
        if node is None:
            self._size += 1
            return _AVLNode(key, value)
        if key < node.key:
            node.left  = self._insert(node.left,  key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value   # chave já existe: atualiza
            return node
        return self._rebalance(node)

    def insert(self, key: str, value: dict):
        """O(log N) garantido pela invariante AVL."""
        self._root = self._insert(self._root, key, value)

    # ── search iterativo ──────────────────────────────────────────────────────
    def search(self, key: str) -> dict:
        """O(log N) garantido. Retorna None se não encontrado."""
        current = self._root
        while current is not None:
            if key == current.key:
                return current.value
            current = current.left if key < current.key else current.right
        return None

    # ── in-order iterativo (pilha explícita) ──────────────────────────────────
    def in_order(self) -> list:
        result  = []
        stack   = []
        current = self._root
        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append({"transaction_id": current.key, **current.value})
            current = current.right
        return result

    def __len__(self):
        return self._size


# ─────────────────────────────────────────────────────────────────────────────
# HASH TABLE  (Account Balances)
# ─────────────────────────────────────────────────────────────────────────────
class HashTable:
    """
    Tabela Hash com encadeamento separado (separate chaining).
    Fator de carga mantido abaixo de 0,75; rehash automático dobra o tamanho.
    Complexidade: get/set/delete O(1) amortizado.
    """

    _INITIAL_CAPACITY = 64
    _LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self):
        self._capacity = self._INITIAL_CAPACITY
        self._buckets  = [[] for _ in range(self._capacity)]
        self._size     = 0

    # ── hash function ─────────────────────────────────────────────────────────
    def _hash(self, key: str) -> int:
        """djb2 hash — distribuição uniforme para strings."""
        h = 5381
        for ch in key:
            h = ((h << 5) + h) + ord(ch)   # h * 33 + ord(ch)
        return h % self._capacity

    # ── rehash ────────────────────────────────────────────────────────────────
    def _rehash(self):
        old_buckets   = self._buckets
        self._capacity *= 2
        self._buckets  = [[] for _ in range(self._capacity)]
        self._size     = 0
        for bucket in old_buckets:
            for k, v in bucket:
                self.set(k, v)

    # ── interface pública ─────────────────────────────────────────────────────
    def set(self, key: str, value):
        """Insere ou atualiza. O(1) amortizado."""
        if self._size / self._capacity >= self._LOAD_FACTOR_THRESHOLD:
            self._rehash()
        idx = self._hash(key)
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._size += 1

    def get(self, key: str):
        """O(1) amortizado. Retorna None se não encontrado."""
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return None

    def delete(self, key: str) -> bool:
        """O(1) amortizado. Retorna True se removido."""
        idx = self._hash(key)
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx].pop(i)
                self._size -= 1
                return True
        return False

    def keys(self):
        for bucket in self._buckets:
            for k, _ in bucket:
                yield k

    def items(self):
        for bucket in self._buckets:
            for k, v in bucket:
                yield k, v

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.get(key) is not None
