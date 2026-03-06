import json
import os

def carregar_bairros():
    """Lê o arquivo JSON gerado pela API e retorna um Conjunto (Set)[cite: 157]."""
    caminho_json = os.path.join('data', 'bairros_slz.json')
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return set(json.load(f)) 
    except FileNotFoundError:
        print("Aviso: Arquivo bairros_slz.json não encontrado.")
        return set()

# DICIONÁRIO: Cadastro Unificado
def carregar_familias():
    caminho_json = os.path.join('data', 'familias_slz.json')
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f) # Dicionário com CPF como chave 
    except FileNotFoundError:
        return {}

# TUPLA: Registro imutável de entregas (Parte 1) 
historico_entregas = (
    ("2026-03-01", "NIS_12345", "Cesta Básica"),
    ("2026-03-02", "NIS_67890", "Auxílio Gás")
)

if __name__ == "__main__":
    bairros_oficiais = carregar_bairros()
    print(f"Estruturas inicializadas.")
    print(f"Total de bairros carregados: {len(bairros_oficiais)}")