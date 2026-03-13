import os
import json


# ── 1. CARREGAMENTO ───────────────────────────────────────────────────────────

def carregar_bairros_coords():
    caminho = os.path.join('data', 'bairros_coords.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError: return []

def carregar_familias():
    caminho = os.path.join('data', 'familias_slz.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError: return {}

def carregar_chuvas():
    caminho = os.path.join('data', 'chuvas_slz.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f: return json.load(f)
    except FileNotFoundError: return []

def carregar_entregas():
    """
    Carrega o histórico de entregas e retorna uma lista de TUPLAS imutáveis
    no formato (data, bairro, quantidade).

    Tuplas são usadas aqui porque cada entrega é um fato histórico:
    não pode ser alterado retroativamente — garante integridade para auditoria.
    """
    caminho = os.path.join('data', 'entregas_sazonais.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        # Converte cada lista [data, bairro, qtd] em tupla imutável
        return [tuple(t) for t in dados.get('tuplas_registro', [])]
    except FileNotFoundError:
        return []


# ── 2. CONJUNTO: bairros atendidos (leitura do campo atendido no JSON) ────────

def construir_conjunto_bairros_atendidos():
    """
    Constrói dinamicamente o SET de bairros já atendidos por algum programa.
    O campo 'atendido' é populado pelo processar_bairros.py no momento da
    extração, cruzando com o familias_slz.json.

    SET justificado:
    - Busca O(1): 'este bairro já é atendido?' é instantâneo
    - Diferença de conjuntos para achar bairros descobertos
    - Elimina duplicatas automaticamente
    """
    bairros = carregar_bairros_coords()
    return {b['nome'] for b in bairros if b.get('atendido')}


# ── 3. MATRIZ: distribuição de cestas por bairro × mês ───────────────────────

def construir_matriz_cestas():
    """
    Constrói uma matriz (lista de listas) onde:
      Linhas  → bairros que aparecem no histórico
      Colunas → meses Jan–Jun (índices 0 a 5)
      Células → total de cestas entregues

    Revela padrões sazonais: jan–jun (período chuvoso) tende a ter picos.
    Retorna (bairros_ordenados, matriz_6_colunas, nomes_meses)
    """
    caminho = os.path.join('data', 'entregas_sazonais.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        bairros   = dados.get('bairros', [])
        matriz    = dados.get('matriz', [])
        meses     = dados.get('meses', [f'Mês {i+1}' for i in range(6)])
        return bairros, matriz, meses
    except FileNotFoundError:
        return [], [], []