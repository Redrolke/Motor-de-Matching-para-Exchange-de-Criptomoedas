#!/usr/bin/env bash
# run.sh — Executa o pipeline completo do Motor de Matching
# Uso: ./run.sh

set -e

echo "======================================"
echo "  Motor de Matching — Exchange BTC/USD"
echo "======================================"
echo ""

# 1. Gera dados de teste
echo "[1/4] Gerando arquivos de entrada..."
python data/generate_data.py
echo ""

# 2. Básico
echo "[2/4] Processando nível BÁSICO..."
python src/main.py \
  --input  data/input_basico.json \
  --output data/output_basico.json \
  --verbose
echo ""

# 3. Avançado
echo "[3/4] Processando nível AVANÇADO..."
python src/main.py \
  --input  data/input_avancado.json \
  --output data/output_avancado.json \
  --verbose
echo ""

# 4. Estresse
echo "[4/4] Processando nível ESTRESSE (100.000 ordens)..."
python src/main.py \
  --input  data/input_estresse.json \
  --output data/output_estresse.json \
  --verbose
echo ""

echo "======================================"
echo "  Concluído! Saídas em /data/"
echo "======================================"
