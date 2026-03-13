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

# DICIONÁRIO: Cadastro Unificado (Parte 1) [cite: 120, 157]
# Atributos baseados diretamente nas variáveis da Tabela 3
cadastro_familias = {
    "NIS_12345": {
        "responsavel": "Maria Silva",
        "bairro": "Coroadinho",
        "membros": 4,
        "renda_sm": 0.5,           # Variável 9 da Tabela 3
        "sem_banheiro": True,      # Variável 6 da Tabela 3
        "analfabetismo": False,    # Variável 8 da Tabela 3
        "inseguranca": "Grave"     # Classificação Parte 2 
    }
}

# CONJUNTO: Bairros atendidos para lógica de exclusão geográfica [cite: 121, 159]
bairros_atendidos = {"Centro", "Anjo da Guarda"} 

# TUPLA: Registro imutável de entregas (Parte 1) 
historico_entregas = (
    ("2026-03-01", "NIS_12345", "Cesta Básica"),
    ("2026-03-02", "NIS_67890", "Auxílio Gás")
)

if __name__ == "__main__":
    bairros_oficiais = carregar_bairros()
    print(f"Estruturas inicializadas.")
    print(f"Total de bairros carregados: {len(bairros_oficiais)}")