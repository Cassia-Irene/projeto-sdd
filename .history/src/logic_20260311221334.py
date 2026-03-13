import os
import json
import s
from datetime import datetime

# ==========================================
# 2. LÓGICA DE CONJUNTOS
# ==========================================
bairros_atendidos = {"Centro", "Cidade Operária", "Cohama", "Jardim Renascença"} 

def identificar_bairros_desassistidos():
    """Usa Teoria de Conjuntos para achar os pontos cegos."""
    dados_bairros = carregar_bairros_coords()
    nomes_totais = {b['nome'] for b in dados_bairros}
    return nomes_totais - bairros_atendidos

# ==========================================
# 3. LÓGICA DE ANÁLISE DE VULNERABILIDADE
# ==========================================
def contar_por_categoria():
    """Gera o resumo para o Gráfico de Pizza."""
    todas = carregar_familias()
    resumo = {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0}
    for d in todas.values():
        cat = d.get("inseguranca", "Seguro")
        resumo[cat] += 1
    return resumo

def calcular_risco_enchente_vs_chuva():
    """Cruza famílias sem infraestrutura com o histórico de chuvas para o Gráfico de Linhas."""
    familias = carregar_familias()
    chuvas = carregar_chuvas()
    
    familias_vulneraveis = sum(1 for d in familias.values() if d['sem_coleta'] or d['sem_banheiro'])
    
    datas, chuva_mm, alerta_familias = [], [], []
    for dia in chuvas:
        if "2026-02" in dia['data'] or "2026-03" in dia['data']: # Pega só os 2 últimos meses
            datas.append(dia['data'])
            mm = dia['chuva_mm']
            chuva_mm.append(mm)
            
            # Se a chuva passar de 15mm, as famílias vulneráveis entram em alerta
            alerta_familias.append(familias_vulneraveis if mm > 15.0 else 0)
            
    return datas, chuva_mm, alerta_familias