import json
import random
import os

# Nomes dos meses para legibilidade
NOMES_MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']

def _chuva_mensal_media(chuvas):
    """
    Agrega os dados diários de chuva em médias mensais para Jan–Jun.
    Retorna uma lista (mm médio por mês).
    """
    acumulado = {m: [] for m in range(6)}  
    for dia in chuvas:
        mes_idx = int(dia['data'][5:7]) - 1  
        if mes_idx < 6:
            acumulado[mes_idx].append(dia['chuva_mm'])
    return [
        round(sum(v) / len(v), 1) if v else 0.0
        for v in acumulado.values()
    ]

def gerar_historico_sazonal_entregas():
    print("📦 Gerando Matriz de Distribuição Sazonal (Jan–Jun)...")

    # Carrega dados base
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)

    with open('data/chuvas_slz.json', 'r', encoding='utf-8') as f:
        chuvas = json.load(f)

    media_chuva_por_mes = _chuva_mensal_media(chuvas)  # [mm_jan, mm_fev, …]

    # ── MATRIZ (lista de listas): Bairros × Meses Jan–Jun
    # Linha  = bairro
    # Coluna = mês (0=Jan … 5=Jun)
    # Célula = cestas entregues naquele bairro naquele mês
    #
    # Lógica sazonal: bairros atendidos recebem base maior; meses com mais
    # chuva (período crítico) recebem um bônus emergencial proporcional.
    matriz_entregas  = []
    historico_tuplas = []   # lista de tuplas (mes, bairro, quantidade)

    for b in bairros:
        linha_bairro = []
        for mes_idx in range(6):
            base         = 15 if b.get('atendido') else 5
            fator_chuva  = int(media_chuva_por_mes[mes_idx] / 10)
            quantidade   = base + fator_chuva + random.randint(0, 10)

            linha_bairro.append(quantidade)

            # TUPLA — Registro histórico
            # (data_referencia, bairro, quantidade)
            historico_tuplas.append(
                (f"2025-{mes_idx+1:02d}", b['nome'], quantidade)
            )

        matriz_entregas.append(linha_bairro)

    # Persiste resultados
    dados_finais = {
        "matriz":           matriz_entregas,
        "tuplas_registro":  historico_tuplas,
        "meses":            NOMES_MESES,
        "bairros":          [b['nome'] for b in bairros]
    }

    os.makedirs('data', exist_ok=True)
    with open('data/entregas_sazonais.json', 'w', encoding='utf-8') as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    print(f"✅ Matriz {len(bairros)}×6 gerada com {len(historico_tuplas)} tuplas de entrega.")
    print(f"   Chuva média por mês: {dict(zip(NOMES_MESES, media_chuva_por_mes))}")

if __name__ == "__main__":
    gerar_historico_sazonal_entregas()