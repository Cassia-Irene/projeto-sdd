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
# Bairros que já possuem ações de entrega ativas
bairros_atendidos = {"Centro", "Cidade Operária", "Cohama", "Jardim Renascença"} 

def identificar_bairros_desassistidos():
    dados_bairros = carregar_bairros_coords()
    nomes_totais = {b['nome'] for b in dados_bairros}
    return nomes_totais - bairros_atendidos

# ==========================================
# 3. LÓGICA DE BUSCA/FILTRO MULTIVARIADO
# ==========================================
def buscar_familias_criticas():
    """
    Filtra famílias cruzando os indicadores da Tabela 3.
    Prioridade: Renda <= 0.5 SM + Vulnerabilidade Sanitária + Sem Auxílio Federal.
    """
    todas_familias = carregar_familias()
    familias_criticas = {}
    
    for cpf, dados in todas_familias.items():
        # Variáveis Sociais e de Infraestrutura
        renda_critica = dados.get("renda_sm", 1.0) <= 0.5    # Var 9
        precariedade = (
            dados.get("sem_banheiro") or                     # Var 6
            dados.get("sem_agua") or                         # Var 5
            dados.get("sem_coleta")                          # Var 7
        )
        
        # Filtro de exclusão: Já recebe auxílio do governo?
        sem_auxilio_federal = not dados.get("ja_recebe_auxilio", False)
        
        # Lógica de decisão: Insegurança Alimentar Grave
        if renda_critica and precariedade and sem_auxilio_federal:
            familias_criticas[cpf] = dados
            
    return familias_criticas

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("="*85)
    print(" 📊 ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR - ANÁLISE INTEGRADA")
    print("="*85)
    
    # 1. Análise de Cobertura Geográfica
    desassistidos = identificar_bairros_desassistidos()
    print(f"\n🌍 [MAPEAMENTO TERRITORIAL]")
    print(f"Total de Bairros Mapeados: {len(carregar_bairros_coords())}")
    print(f"Bairros Desassistidos (Pontos Cegos): {len(desassistidos)}")
    
    # 2. Identificação de Alvos Prioritários
    criticas = buscar_familias_criticas()
    print(f"\n⚠️ [IDENTIFICAÇÃO DE FAMÍLIAS CRÍTICAS - TABELA 3]")
    print(f"Total de Famílias no Cadastro: {len(carregar_familias())}")
    print(f"Casos de Prioridade Urgente (Filtro Multivariado): {len(criticas)}")
    print("-" * 85)
    
    if criticas:
        print(f"{'RESPONSÁVEL':<25} | {'BAIRRO':<20} | {'RENDA':<8} | {'COORDENADAS'}")
        for i, (cpf, f) in enumerate(criticas.items()):
            if i < 8: # Mostra as top 8 para o professor ver a variedade
                coords = f"{f['latitude']:.4f}, {f['longitude']:.4f}"
                print(f" {f['responsavel']:<25} | {f['bairro']:<20} | {f['renda_sm']:<5} SM | {coords}")
    
    print("\n" + "="*85)