# ==========================================
# 1. FUNÇÕES DE CARREGAMENTO (Podem ir para structures.py depois, mas manteremos aqui por simplicidade agora)
# ==========================================
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