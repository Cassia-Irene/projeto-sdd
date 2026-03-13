import os
import json

# ==========================================
# 1. FUNÇÕES AUXILIARES DE CARREGAMENTO
# ==========================================
def carregar_bairros_coords():
    """Carrega o novo JSON com Nome, Lat e Lng."""
    caminho = os.path.join('data', 'bairros_coords.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f) # Retorna lista de dicts
    except FileNotFoundError:
        print("Erro: bairros_coords.json não encontrado.")
        return []

def carregar_familias():
    caminho = os.path.join('data', 'familias_slz.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ==========================================
# 2. LÓGICA DE CONJUNTOS (PARTE 2)
# ==========================================
bairros_atendidos = {"Centro", "Cidade Operária", "Cohama", "Jardim Renascença"} 

def identificar_bairros_desassistidos():
    """Extrai nomes dos bairros georreferenciados para calcular pontos cegos."""
    dados_bairros = carregar_bairros_coords()
    # Criamos um SET apenas com os nomes para permitir a operação de diferença
    nomes_totais = {b['nome'] for b in dados_bairros}
    
    return nomes_totais - bairros_atendidos

# ==========================================
# 3. LÓGICA DE BUSCA/FILTRO (PARTE 2)
# ==========================================
def buscar_familias_criticas():
    """Filtra o dicionário cruzando renda, saneamento e infraestrutura (Tabela 3)."""
    todas_familias = carregar_familias()
    familias_criticas = {}
    
    for cpf, dados in todas_familias.items():
        # Variáveis da Tabela 3
        renda_critica = dados.get("renda_sm", 1.0) <= 0.5    # Variável 9
        sem_banheiro = dados.get("sem_banheiro", False)    # Variável 6
        sem_agua = dados.get("sem_agua", False)            # Variável 5
        sem_lixo = dados.get("sem_coleta", False)          # Variável 7
        
        # O critério agora é multivariado (Saneamento Básico Precário)
        if renda_critica and (sem_banheiro or sem_agua or sem_lixo):
            familias_criticas[cpf] = dados
            
    return familias_criticas

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("="*80)
    print(" 📊 ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR - ANÁLISE GEORREFERENCIADA")
    print("="*80)
    
    desassistidos = identificar_bairros_desassistidos()
    print(f"\n🌍 [MAPEAMENTO GEOGRÁFICO]")
    print(f"Total de Bairros (Kaggle Hub): {len(carregar_bairros_coords())}")
    print(f"Pontos Cegos para Mapa de Calor: {len(desassistidos)}")
    
    criticas = buscar_familias_criticas()
    print(f"\n⚠️ [MAPEAMENTO FAMILIAR - CASOS CRÍTICOS (TABELA 3)]")
    print(f"Famílias em Risco (Renda <= 0.5 SM + Infraestrutura Precária): {len(criticas)}")
    print("-" * 80)
    
    if criticas:
        # Mostra os 5 primeiros para conferência
        for i, (cpf, f) in enumerate(criticas.items()):
            if i < 5:
                print(f" -> {f['responsavel']} | Bairro: {f['bairro']}")
                print(f"    Renda: {f['renda_sm']} SM | Banheiro: {f.get('sem_banheiro')} | Água: {f.get('sem_agua')}")
    print("="*80)