import json
import os

def carregar_bairros():
    """
    Lê o arquivo JSON gerado pela API e retorna um (Set).
    """
    caminho_json = os.path.join('data', 'bairros_slz.json')
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            lista_bairros = json.load(f)
            return set(lista_bairros) # Transformação em Conjunto para operações de diferença 
    except FileNotFoundError:
        print("Aviso: Arquivo bairros_slz.json não encontrado. Rode o script em /data primeiro.")
        return set()

# DICIONÁRIO: Estrutura principal para o Cadastro Unificado (Parte 1) [cite: 120, 157]
# Chave: CPF ou NIS (String)
# Valor: Dicionário com atributos de vulnerabilidade [cite: 158]
cadastro_familias = {
    "123.456.789-00": {
        "nome_responsavel": "Exemplo Silva",
        "bairro": "Coroadinho",
        "renda_per_capita": 350.00, # Variável da Tabela 3
        "membros": 5,
        "inseguranca": "Grave", # Níveis: Seguro, Leve, Moderado, Grave [cite: 158]
        "area_risco": True # Foco em palafitas/ribeirinhas [cite: 116]
    }
}

# CONJUNTO: Bairros que já receberam algum auxílio municipal [cite: 121]
bairros_atendidos = {"Centro", "Anjo da Guarda"} 

# TUPLA: Registro imutável de entregas para auditoria (Data, Bairro, Quantidade) 
historico_entregas = (
    ("2026-02-10", "Vila Bacanga", 50),
    ("2026-02-15", "Cidade Operária", 30)
)

if __name__ == "__main__":
    bairros_oficiais = carregar_bairros()
    print(f"Estruturas inicializadas.")
    print(f"Total de bairros no Conjunto: {len(bairros_oficiais)}")