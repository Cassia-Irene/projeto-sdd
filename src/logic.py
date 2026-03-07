import os
import json

# ==========================================
# 1. FUNÇÕES AUXILIARES DE CARREGAMENTO
# ==========================================
def carregar_bairros():
    """Carrega o JSON de bairros gerado pelo Kaggle/Pandas e retorna um SET."""
    caminho = os.path.join('data', 'bairros_slz.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        print("Erro: bairros_slz.json não encontrado.")
        return set()

def carregar_familias():
    """Carrega o JSON de famílias gerado pelo script."""
    caminho = os.path.join('data', 'familias_slz.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Erro: familias_slz.json não encontrado.")
        return {}

# ==========================================
# 2. LÓGICA DE CONJUNTOS (PARTE 2)
# ==========================================
# Simulação de bairros que já receberam alguma cesta básica este mês
bairros_atendidos = {"Centro", "Cidade Operária", "Cohama", "Renascença"} 

def identificar_bairros_desassistidos():
    """Usa Diferença de Conjuntos para achar bairros oficiais sem atendimento."""
    bairros_totais = carregar_bairros()
    # A mágica dos Conjuntos em Python: Operador '-'
    bairros_esquecidos = bairros_totais - bairros_atendidos 
    return bairros_esquecidos

# ==========================================
# 3. LÓGICA DE BUSCA/FILTRO (PARTE 2)
# ==========================================
def buscar_familias_criticas():
    """Filtra o dicionário buscando famílias em situação extrema."""
    todas_familias = carregar_familias()
    familias_criticas = {}
    
    for cpf, dados in todas_familias.items():
        # Regras baseadas na Tabela 3: Renda muito baixa E sem saneamento
        renda_critica = dados.get("renda_sm", 1.0) <= 0.5 
        sem_banheiro = dados.get("sem_banheiro", False)
        
        # Só entra se for caso extremo
        if renda_critica and sem_banheiro:
            familias_criticas[cpf] = dados
            
    return familias_criticas

# ==========================================
# 4. LÓGICA DE PRIORIZAÇÃO (ORDENAÇÃO)
# ==========================================
def converter_dict_para_lista(dicionario_familias):
    """Converte o dicionário de CPFs numa lista para o algoritmo Merge Sort."""
    familias_lista = []
    for cpf, info in dicionario_familias.items():
        familia = {"cpf": cpf}
        familia.update(info)
        familias_lista.append(familia)
    return familias_lista

def filtrar_por_bairro(familias_ordenadas, bairro_alvo, bairros_validos):
    """Filtra a lista já ordenada pelo Merge Sort para um bairro específico."""
    if bairro_alvo not in bairros_validos:
        print(f"Aviso: O bairro '{bairro_alvo}' não consta na lista oficial.")
        return []
    return [f for f in familias_ordenadas if f.get('bairro') == bairro_alvo]

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("="*80)
    print(" 📊 ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR - ANÁLISE")
    print("="*80)
    
    # Executa Análise Geográfica
    desassistidos = identificar_bairros_desassistidos()
    print(f"\n🌍 [MAPEAMENTO GEOGRÁFICO]")
    print(f"Total de Bairros (Kaggle): {len(carregar_bairros())}")
    print(f"Bairros Atendidos: {len(bairros_atendidos)}")
    print(f"Pontos Cegos (Desassistidos): {len(desassistidos)}")
    
    # Executa Análise Familiar
    criticas = buscar_familias_criticas()
    print(f"\n⚠️ [MAPEAMENTO FAMILIAR - CASOS CRÍTICOS]")
    print(f"Total de Famílias Cadastradas: {len(carregar_familias())}")
    print(f"Famílias em Situação Crítica (Renda <= 0.5 SM e Sem Banheiro): {len(criticas)}")
    print("-" * 80)
    
    # Exibe os resultados críticos formatados
    if not criticas:
        print("Nenhuma família em situação crítica encontrada nos critérios atuais.")
    else:
        for cpf, f in criticas.items():
            print(f" -> {f['responsavel']} | Bairro: {f['bairro']} | Renda: {f['renda_sm']} SM")
    print("="*80)