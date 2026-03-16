from src.structures import (
    carregar_bairros_coords, carregar_familias, carregar_chuvas, construir_conjunto_bairros_atendidos
)

# Limiar único
LIMIAR_CHUVA_EMERGENCIAL_MM = 15.0

# 1. CONJUNTOS: cobertura territorial

def identificar_bairros_desassistidos():
    """
    Operação de DIFERENÇA entre conjuntos:
      todos_os_bairros  -  bairros_atendidos  =  bairros_descobertos

    Complexidade O(n)
    """
    dados_bairros    = carregar_bairros_coords()
    nomes_totais     = {b['nome'] for b in dados_bairros}
    bairros_atendidos = construir_conjunto_bairros_atendidos()
    return nomes_totais - bairros_atendidos


# 2. ANÁLISE DE VULNERABILIDADE 

def contar_por_categoria():
    #Conta famílias por nível de insegurança alimentar.
    todas = carregar_familias()
    resumo = {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0}
    for d in todas.values():
        resumo[d.get("inseguranca","Seguro")] += 1
    return resumo


def calcular_risco_enchente_vs_chuva():
    """
    Cruza famílias em situação de risco (Grave ou Moderada) com o histórico de chuvas. Quando a precipitação supera 15mm/dia,
    aciona o protocolo de alerta de estoque emergencial.
    """
    familias = carregar_familias()
    chuvas   = carregar_chuvas()

    # Famílias em risco real (Grave ou Moderada)
    familias_em_risco = sum(
        1 for d in familias.values()
        if d.get('inseguranca') in ('Grave', 'Moderada')
    )

    datas, chuva_mm, alerta_familias = [], [], []
    for dia in chuvas:
        datas.append(dia['data'])
        mm = dia['chuva_mm']
        chuva_mm.append(mm)
        # Limiar: chuva > 15mm dispara alerta de distribuição emergencial
        alerta_familias.append(familias_em_risco if mm > LIMIAR_CHUVA_EMERGENCIAL_MM else 0)

    return datas, chuva_mm, alerta_familias

def resumo_vulnerabilidade_por_territorio():

    familias = carregar_familias()
    resultado = {
        1: {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0, "renda_pc": [], "membros": []},
        2: {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0, "renda_pc": [], "membros": []},
        3: {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0, "renda_pc": [], "membros": []},
    }

    for d in familias.values():
        vuln = d.get('vulnerabilidade_territorial', 2)
        if vuln not in resultado:
            continue
        resultado[vuln][d.get('inseguranca', 'Seguro')] += 1
        resultado[vuln]['renda_pc'].append(d.get('renda_pc_sm', 0))
        resultado[vuln]['membros'].append(d.get('membros', 3))

    for nivel in resultado:
        rpc = resultado[nivel].pop('renda_pc')
        mb = resultado[nivel].pop('membros')
        resultado[nivel]['media_renda_pc'] = round(sum(rpc) / len(rpc), 3) if rpc else 0
        resultado[nivel]['media_membros']  = round(sum(mb) / len(mb), 2) if mb else 0
    
    return resultado


# 3. LÓGICA ESPACIAL

def obter_dados_mapa_calor():
    """
    Retorna lats, lngs e níveis de risco para o HeatMap.
    O peso combina nível de insegurança da família com vulnerabilidade territorial do bairro.
    """

    familias = carregar_familias()
    bairros_coords = carregar_bairros_coords()

    # Lookup O(1): bairro → vulnerabilidade territorial
    vuln_dict = {
        b['nome']: b.get('vulnerabilidade_territorial', 2)
        for b in bairros_coords
    }

    pesos_inseguranca = {'Grave': 1.0, 'Moderada': 0.6, 'Leve': 0.2, 'Seguro': 0.1}
    fator_territorial = {3: 1.5, 2: 1.0, 1: 0.6}

    lats, lngs, pesos = [], [], []

    for dados in familias.values():
        lats.append(dados['latitude'])
        lngs.append(dados['longitude'])
        niveis_risco.append(dados['inseguranca'])
    return lats, lngs, niveis_risco