from datetime import datetime

# 1. IMPORTAÇÕES DE DADOS
from src.structures import carregar_bairros_coords, carregar_familias, carregar_chuvas


# 2. LÓGICA DE CONJUNTOS
bairros_atendidos = {"Centro", "Cidade Operária", "Cohama", "Jardim Renascença"} 

def identificar_bairros_desassistidos():
    dados_bairros = carregar_bairros_coords()
    nomes_totais = {b['nome'] for b in dados_bairros}
    return nomes_totais - bairros_atendidos


# 3. LÓGICA DE ANÁLISE DE VULNERABILIDADE
def contar_por_categoria():

    todas = carregar_familias()
    resumo = {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0}
    for d in todas.values():
        cat = d.get("inseguranca", "Seguro")
        resumo[cat] += 1
    return resumo

def calcular_risco_enchente_vs_chuva():
    
    #Cruza famílias sem infraestrutura com o histórico de chuvas.
    
    familias = carregar_familias()
    chuvas = carregar_chuvas()
    
    familias_vulneraveis = sum(1 for d in familias.values() if d['sem_coleta'] or d['sem_banheiro'])
    
    datas, chuva_mm, alerta_familias = [], [], []
    for dia in chuvas:
        datas.append(dia['data'])
        mm = dia['chuva_mm']
        chuva_mm.append(mm)
            
        # Se a chuva passar de 15mm, aciona o alerta de estoque emergencial
        
        alerta_familias.append(familias_vulneraveis if mm > 15.0 else 0)
            
    return datas, chuva_mm, alerta_familias

# 4. LÓGICA ESPACIAL (MAPA DE CALOR)
def obter_dados_mapa_calor():
    familias = carregar_familias()
    
    lats = []
    lngs = []
    niveis_risco = []
    
    for dados in familias.values():
        lats.append(dados['latitude'])
        lngs.append(dados['longitude'])
        niveis_risco.append(dados['inseguranca'])
        
    return lats, lngs, niveis_risco