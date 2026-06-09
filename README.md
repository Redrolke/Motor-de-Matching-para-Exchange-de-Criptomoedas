# 🔁 Motor de Matching para Exchange de Criptomoedas

**Projeto 7 — Estruturas de Dados e Algoritmos**

> Motor de Order Book para cruzamento instantâneo de ordens de compra e venda de BTC/USD.
> Todas as estruturas de dados foram implementadas manualmente, sem bibliotecas de alto nível.

---

## 👥 Membros da Equipe

| Nome | GitHub | Responsabilidade |
|------|--------|-----------------|
| *(Adicionar)* | @usuario | *(Adicionar)* |

---

## 📁 Estrutura do Repositório

```
/
├── src/
│   ├── structures.py     # MaxHeap, MinHeap, BST, HashTable (do zero)
│   ├── order_book.py     # Motor de Matching (Price-Time Priority)
│   └── main.py           # Ponto de entrada CLI
├── data/
│   ├── generate_data.py  # Gerador de input_basico/avancado/estresse
│   ├── input_basico.json
│   ├── input_avancado.json
│   └── input_estresse.json
├── docs/
│   └── complexidade.md   # Análise detalhada de complexidade
├── run.sh
└── README.md
```

---

## ⚙️ Requisitos

- **Python 3.8+** (sem dependências externas para execução)
- `uuid`, `json`, `random`, `time` — apenas para geração de dados (stdlib)

---

## 🚀 Execução

### 1. Gerar os arquivos de teste

```bash
python data/generate_data.py
```

### 2. Processar os cenários

```bash
# Nível básico
python src/main.py --input data/input_basico.json --output data/output_basico.json --verbose

# Nível avançado
python src/main.py --input data/input_avancado.json --output data/output_avancado.json --verbose

# Teste de estresse (100.000 ordens)
python src/main.py --input data/input_estresse.json --output data/output_estresse.json --verbose
```

### Ou via script padrão

```bash
chmod +x run.sh
./run.sh
```

---

## 📐 Estruturas de Dados (Implementadas do Zero)

| Estrutura    | Classe       | Requisito | Complexidade          |
|:------------|:------------|:---------|:----------------------|
| **Max-Heap** | `MaxHeap`   | RF01     | Insert/Extract O(log N) |
| **Min-Heap** | `MinHeap`   | RF01     | Insert/Extract O(log N) |
| **BST**      | `BST`       | RF02     | Search/Insert O(log N)  |
| **HashTable**| `HashTable` | RF03     | Get/Set O(1) amortizado |

### Por que essas escolhas?

- **MaxHeap para compras:** O comprador com maior preço tem prioridade → acesso
  em O(1) ao topo, remoção em O(log N).
- **MinHeap para vendas:** O vendedor com menor preço tem prioridade → mesma lógica simétrica.
- **BST para histórico:** Buscas por `transaction_id` em O(log N) para auditoria.
- **HashTable para saldos:** Atualizações a cada trade exigem O(1) — hash com djb2 + chaining.

---

## 🔄 Algoritmo de Matching

O motor implementa **Price-Time Priority** (padrão de exchanges reais):

```
Para cada ordem de COMPRA com preço P:
  Enquanto (MinHeap não vazio) e (P >= venda_mais_barata.preço):
    1. Extrair venda mais barata do MinHeap         → O(log N)
    2. Calcular quantidade negociada (min das duas)
    3. Executar trade → atualizar HashTable         → O(1)
    4. Registrar transação na BST                  → O(log N)
    5. Reinserir saldo da venda (se parcial)        → O(log N)
  Inserir saldo da compra no MaxHeap (se não zerado) → O(log N)

Complexidade total para N ordens: O(N log N)
```

---

## 📊 Métricas do Teste de Estresse

| Métrica              | Valor       |
|---------------------|-------------|
| Total de ordens      | 100.000     |
| Contas distintas     | 500         |
| Complexidade total   | O(N log N)  |
| Memória estimada     | < 200 MB    |

---

## 📄 Formato de Entrada

```json
{
  "metadata": { "level": "basico" },
  "initial_balances": {
    "ACC_001": { "BTC": 5.0, "USD": 500000.0 }
  },
  "orders": [
    {
      "order_id": "uuid-v4",
      "account_id": "ACC_001",
      "side": "buy",
      "price": 50000.00,
      "quantity": 0.5,
      "timestamp": 1717789200000
    }
  ]
}
```

## 📄 Formato de Saída

```json
{
  "summary": {
    "total_orders_processed": 20,
    "total_transactions": 8,
    "open_buy_orders": 3,
    "open_sell_orders": 2,
    "processing_time_seconds": 0.003
  },
  "transactions": [ ... ],
  "open_orders": { "buy_orders": [...], "sell_orders": [...] },
  "final_balances": { "ACC_001": { "BTC": 4.5, "USD": 525000.0 } }
}
```

---

## 🔍 Documentação Técnica

Veja [`docs/complexidade.md`](docs/complexidade.md) para análise completa de:
- Justificativa de cada estrutura
- Invariantes das heaps
- Política de rehash da HashTable
- Análise de memória
- Decisões de projeto
