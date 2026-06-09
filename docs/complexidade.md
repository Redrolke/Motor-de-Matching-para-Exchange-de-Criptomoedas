# Documentação Técnica — Projeto 7: Motor de Matching para Exchange de Criptomoedas

## 1. Visão Geral

Este projeto implementa o núcleo algorítmico de uma exchange de criptomoedas,
processando um *Order Book* de compra e venda de BTC/USD via linha de comando.

**Nenhuma biblioteca de alto nível foi utilizada** para as estruturas de dados centrais.
Todas as implementações partem do zero sobre listas nativas do Python.

---

## 2. Estruturas de Dados Implementadas

### 2.1 Max-Heap — Ordens de Compra (RF01)

**Arquivo:** `src/structures.py` → classe `MaxHeap`

**Justificativa:** Em um Order Book, a ordem de compra com **maior preço** tem
prioridade máxima (o comprador mais disposto a pagar deve ser atendido primeiro).
O Max-Heap garante acesso e remoção desse elemento em O(log N).

**Invariante:** Para todo nó `i`, `price[i] >= price[filho_esquerdo(i)]` e `>= price[filho_direito(i)]`.

**Critério de desempate:** Quando dois compradores oferecem o mesmo preço, a ordem
que chegou primeiro (menor `timestamp`) tem prioridade — *FIFO* por nível de preço.

| Operação     | Complexidade |
|--------------|-------------|
| `insert`     | O(log N)    |
| `extract_max`| O(log N)    |
| `peek`       | O(1)        |

---

### 2.2 Min-Heap — Ordens de Venda (RF01)

**Arquivo:** `src/structures.py` → classe `MinHeap`

**Justificativa:** Em contrapartida, a ordem de venda com **menor preço** tem
prioridade máxima (o vendedor disposto a vender mais barato é atendido primeiro).
O Min-Heap é o espelho simétrico do Max-Heap com comparação invertida.

| Operação     | Complexidade |
|-------------|-------------|
| `insert`    | O(log N)    |
| `extract_min`| O(log N)   |
| `peek`      | O(1)        |

---

### 2.3 AVL Tree — Histórico de Transações (RF02)

**Arquivo:** `src/structures.py` → classe `BST` (implementada como AVL Tree)

**Justificativa:** O histórico de transações exige buscas frequentes por `transaction_id`
(auditoria, reconciliação). A AVL Tree garante **O(log N) no pior caso** para inserção
e busca — fundamental neste projeto, pois os IDs são gerados sequencialmente
(`TX00000001`, `TX00000002`, ...). Uma BST simples com chaves crescentes degenera
para uma lista encadeada (altura O(N)), tornando operações O(N).

**Invariante AVL:** Para todo nó, |altura(subárvore esquerda) − altura(subárvore direita)| ≤ 1.

**Rotações implementadas:** LL, RR, LR, RL — executadas automaticamente após cada inserção.

**Resultado medido:** Com 50.000 chaves sequenciais, a AVL mantém altura 16 (log₂(50000) ≈ 15).

| Operação  | Complexidade Garantida |
|-----------|----------------------|
| `insert`  | O(log N)             |
| `search`  | O(log N)             |
| `in_order`| O(N)                 |

---

### 2.4 Tabela Hash — Saldos de Contas (RF03)

**Arquivo:** `src/structures.py` → classe `HashTable`

**Justificativa:** Saldos de contas são acessados e atualizados a cada transação.
O tempo deve ser O(1) amortizado — a HashTable com encadeamento separado satisfaz
esse requisito.

**Função de hash:** *djb2* — reconhecida por boa distribuição em strings arbitrárias.

**Política de rehash:** Quando o fator de carga ultrapassa 0,75, a tabela dobra
sua capacidade e realoca todos os pares. Essa operação é O(N) mas ocorre raramente
(a cada duplicação), resultando em O(1) amortizado.

**Resolução de colisões:** Encadeamento separado (listas por bucket).

| Operação | Complexidade Amortizada |
|----------|------------------------|
| `set`    | O(1)                   |
| `get`    | O(1)                   |
| `delete` | O(1)                   |

---

## 3. Algoritmo de Matching

O motor de matching (`src/order_book.py`) implementa o algoritmo **Price-Time Priority**,
padrão em exchanges reais (NYSE, Binance, Coinbase).

### Fluxo de uma ordem de COMPRA

```
1. Peek no topo do MinHeap (venda mais barata)
2. Se buy.price >= sell.price → MATCH
   a. traded_qty  = min(buy.qty, sell.qty)
   b. traded_price = sell.price  (preço da ordem passiva)
   c. Executar trade: atualizar HashTable de saldos
   d. Registrar transação na BST
   e. Reinserir saldo da venda (se parcial) no MinHeap → O(log N)
   f. Repetir até sem match ou quantidade zerada
3. Saldo não executado → inserir no MaxHeap → O(log N)
```

### Complexidade por Ordem

| Cenário              | Complexidade       |
|----------------------|--------------------|
| Sem match            | O(log N)           |
| 1 match completo     | O(log N)           |
| K matches parciais   | O(K log N)         |
| Fluxo total (N ordens)| O(N log N)        |

Isso atende diretamente o requisito **O(N log N)** do enunciado.

---

## 4. Formato dos Arquivos

### Entrada (`input_*.json`)

```json
{
  "metadata": { "level": "basico" },
  "initial_balances": {
    "ACC_001": { "BTC": 5.0, "USD": 500000.0 }
  },
  "orders": [
    {
      "order_id": "uuid",
      "account_id": "ACC_001",
      "side": "buy",
      "price": 50000.00,
      "quantity": 0.5,
      "timestamp": 1717789200000
    }
  ]
}
```

### Saída (`output_*.json`)

```json
{
  "summary": {
    "total_orders_processed": 20,
    "total_transactions": 8,
    "open_buy_orders": 3,
    "open_sell_orders": 2
  },
  "transactions": [ ... ],
  "open_orders": { "buy_orders": [...], "sell_orders": [...] },
  "final_balances": { "ACC_001": { "BTC": 4.5, "USD": 525000.0 } }
}
```

---

## 5. Análise de Memória

| Estrutura  | Espaço    | Observação                                  |
|------------|-----------|---------------------------------------------|
| MaxHeap    | O(N)      | Lista contígua — cache-friendly             |
| MinHeap    | O(N)      | Idem                                        |
| BST        | O(N)      | Ponteiros por nó (_BSTNode com __slots__)   |
| HashTable  | O(N)      | Rehash automático controla fator de carga   |

Para o teste de estresse com 100.000 ordens e 500 contas, a memória total estimada
é inferior a **200 MB**, bem dentro dos limites práticos de execução.

---

## 6. Decisões de Projeto

- **Python puro:** Compatibilidade universal, sem dependências externas.
- **`__slots__` no BSTNode:** Reduz overhead de memória por nó (~40% vs dict).
- **Comparação por `(price, timestamp)`:** Garante determinismo no desempate.
- **Precisão de 8 casas decimais:** Padrão Bitcoin (1 satoshi = 0,00000001 BTC).
- **Saída determinística:** Transações e ordens abertas ordenadas por ID, garantindo
  que o mesmo input sempre produza exatamente o mesmo output.
