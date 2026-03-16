from src.structures import (
    carregar_bairros_coords, carregar_familias, carregar_chuvas,
    construir_conjunto_bairros_atendidos
)


# ── 1. CONJUNTOS: cobertura territorial ───────────────────────────────────────

def identificar_bairros_desassistidos():
    """
    Operação de DIFERENÇA entre conjuntos:
      todos_os_bairros  -  bairros_atendidos  =  bairros_descobertos

    Complexidade O(n) — muito mais eficiente que comparar listas aninhadas.
    """
    dados_bairros    = carregar_bairros_coords()
    nomes_totais     = {b['nome'] for b in dados_bairros}
    bairros_atendidos = construir_conjunto_bairros_atendidos()
    return nomes_totais - bairros_atendidos


# ── 2. ANÁLISE DE VULNERABILIDADE ─────────────────────────────────────────────

def contar_por_categoria():
    """Conta famílias por nível de insegurança alimentar."""
    todas = carregar_familias()
    resumo = {"Grave": 0, "Moderada": 0, "Leve": 0, "Seguro": 0}
    for d in todas.values():
        cat = d.get("inseguranca", "Seguro")
        resumo[cat] += 1
    return resumo


def calcular_risco_enchente_vs_chuva():
    """
    Cruza famílias em situação de risco (Grave ou Moderada) com o
    histórico de chuvas. Quando a precipitação supera 15mm/dia,
    aciona o protocolo de alerta de estoque emergencial.

    Substituição das antigas variáveis de saneamento (sem_coleta,
    sem_banheiro) pelo indicador de insegurança alimentar diretamente —
    metodologicamente mais coerente com o objetivo do sistema.
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
        alerta_familias.append(familias_em_risco if mm > 15.0 else 0)

    return datas, chuva_mm, alerta_familias


# ── 3. LÓGICA ESPACIAL ────────────────────────────────────────────────────────

def obter_dados_mapa_calor():
    """Retorna lats, lngs e níveis de risco para o HeatMap."""
def obter_dados_mapa_calor():
    """
    Retorna lats, lngs e pesos de risco para o HeatMap.
    O peso combina o nível de insegurança alimentar da família
    com a vulnerabilidade territorial do bairro onde ela mora.
    """
    familias      = carregar_familias()
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
        bairro = dados.get('bairro')
        nivel  = dados.get('inseguranca', 'Seguro')
        vuln   = vuln_dict.get(bairro, 2)

        peso = pesos_inseguranca.get(nivel, 0.1) * fator_territorial.get(vuln, 1.0)

        lats.append(dados['latitude'])
        lngs.append(dados['longitude'])
        pesos.append(peso)

    return lats, lngs, pesos