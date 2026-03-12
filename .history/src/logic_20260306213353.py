import os
import json

# ==========================================
# 1. FUNÇÕES AUXILIARES DE CARREGAMENTO
# ==========================================
def carregar_bairros_coords():
    """Carrega o JSON de coordenadas para análise geográfica."""
    caminho = os.path.join('data', 'bairros_coords.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
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
# Bairros que já possuem ações de entrega ativas para teste de diferença
bairros_atendidos = {"Centro", "Cidade Operária", "Cohama", "Jardim Renascença"} 

def identificar_bairros_desassistidos():
    dados_bairros = carregar_bairros_coords()
    nomes_totais = {b['nome'] for b in dados_bairros}
    return nomes_totais - bairros_atendidos

# ==========================================
# 3. LÓGICA DE FILTRAGEM E RESUMO
# ==========================================
def buscar_familias_por_nivel(nivel="Grave"):
    """Filtra famílias pelo nível de insegurança gerado no familias.py."""
    todas_familias = carregar_familias()
    return {cpf: d for cpf, d in todas_familias.items() if d.get("inseguranca") == nivel}

def contar_por_categoria():
    """Gera um resumo estatístico das categorias para o Dashboard."""
    todas = carregar_familias()
    resumo = {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0}
    for d in todas.values():
        cat = d.get("inseguranca", "Seguro")
        resumo[cat] += 1
    return resumo

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("="*95)
    print(" 📊 ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR - ANÁLISE INTEGRADA (TABELA 3)")
    print("="*95)
    
    # 1. Cobertura Geográfica
    desassistidos = identificar_bairros_desassistidos()
    print(f"\n🌍 [MAPEAMENTO TERRITORIAL]")
    print(f"Total de Bairros Base: {len(carregar_bairros_coords())}")
    print(f"Bairros Atendidos: {len(bairros_atendidos)}")
    print(f"Pontos Cegos (Aguardando Atendimento): {len(desassistidos)}")
    
    # 2. Resumo de Insegurança
    stats = contar_por_categoria()
    print(f"\n📈 [RESUMO DE SEGURANÇA ALIMENTAR]")
    for cat, total in stats.items():
        print(f" - {cat:<10}: {total} famílias")
    
    # 3. Lista de Prioridade Urgente
    criticas = buscar_familias_por_nivel("Grave")
    print(f"\n⚠️ [IDENTIFICAÇÃO DE PRIORIDADE MÁXIMA - CLASSIFICAÇÃO GRAVE]")
    print(f"Critério: Renda <= 0.3 SM + Privação de Infraestrutura (Variáveis 5, 6 ou 7)")
    print("-" * 95)
    
    if criticas:
        header = f"{'RESPONSÁVEL':<22} | {'BAIRRO':<18} | {'RENDA':<6} | {'COORDENADAS':<20} | {'AUXÍLIO'}"
        print(header)
        for i, (cpf, f) in enumerate(criticas.items()):
            if i < 10: # Mostra as 10 primeiras para conferência
                coords = f"{f['latitude']:.4f}, {f['longitude']:.4f}"
                auxilio = "Sim" if f.get('ja_recebe_auxilio') else "Não"
                print(f" {f['responsavel']:<22} | {f['bairro']:<18} | {f['renda_sm']:<5} | {coords:<20} | {auxilio}")
    else:
        print("Nenhuma família com insegurança GRAVE detectada nesta amostra.")
    
    print("\n" + "="*95)