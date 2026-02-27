# main.py
import csv
from api_transparencia import obter_conjunto_assistidos

# =====================================================================
# 1. CADASTRO UNIFICADO COM DICIONÁRIOS (Lendo do CSV)
# =====================================================================
cadastro_bairros = {}

print("Lendo a base de dados do CadÚnico e montando Dicionários...")

# Abrindo o arquivo CSV que criamos
with open('dados_cadunico.csv', mode='r', encoding='utf-8') as arquivo:
    leitor = csv.DictReader(arquivo)
    
    for linha in leitor:
        bairro = linha['bairro']
        risco_enchente = True if linha['risco_enchente'] == 'Sim' else False
        nis = linha['nis']
        renda = float(linha['renda_per_capita'])
        
        # Se o bairro ainda não existe no nosso dicionário, criamos a estrutura dele
        if bairro not in cadastro_bairros:
            cadastro_bairros[bairro] = {
                "risco_enchente": risco_enchente,
                "total_familias": 0,
                "nis_vulneraveis": set() # Inicializa o Conjunto vazio
            }
        
        # Incrementa o total de famílias daquele bairro
        cadastro_bairros[bairro]["total_familias"] += 1
        
        # Regra de Negócio: Se a renda for menor que R$ 109 (linha da extrema pobreza), entra no conjunto de vulneráveis
        if renda < 109.00:
            cadastro_bairros[bairro]["nis_vulneraveis"].add(nis)

# =====================================================================
# 2. MAPEAMENTO DE EXCLUSÃO COM CONJUNTOS (SETS)
# =====================================================================

# Passo A: Juntar todos os NIS vulneráveis (Conjunto A)
todas_familias_vulneraveis = set()
for bairro, dados in cadastro_bairros.items():
    todas_familias_vulneraveis = todas_familias_vulneraveis.union(dados["nis_vulneraveis"])

# Passo B: Pegar os dados da API (Conjunto B - Famílias assistidas)
# (Se a API do código anterior estiver com erro, ele vai usar o conjunto de teste {"111", "333", "555"})
familias_assistidas = obter_conjunto_assistidos()

# Passo C: A Mágica dos Conjuntos! (Subtração: Quem precisa - Quem já recebe)
familias_esquecidas = todas_familias_vulneraveis - familias_assistidas

# =====================================================================
# 3. ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR (Resultados)
# =====================================================================

print("\n" + "="*50)
print(" RELATÓRIO DO ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR")
print("="*50)
print(f"Famílias em extrema pobreza (Conjunto A): {len(todas_familias_vulneraveis)}")
print(f"Famílias recebendo auxílio (Conjunto B): {len(familias_assistidas)}")
print("-" * 50)
print(f"🚨 ALERTA CRÍTICO: Famílias desamparadas: {len(familias_esquecidas)}")
print(f"NIS para busca ativa imediata: {familias_esquecidas}")
print("="*50)

# Demonstração do Dicionário para os professores:
print("\n[Busca rápida no Dicionário O(1)]")
print(f"Situação no Coroadinho: {cadastro_bairros['Coroadinho']}")