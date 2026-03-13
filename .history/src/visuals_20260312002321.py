import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import folium
from folium.plugins import HeatMap
import io
import base64
import os
from src.logic import contar_por_categoria, calcular_risco_enchente_vs_chuva, obter_dados_mapa_calor
from src.structures import carregar_bairros_coords 

def _plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close(fig) 
    return base64.b64encode(buf.read()).decode('utf-8')

def gerar_dashboard_html():
    print("Gerando visualizações estratégicas...")
    
    # 1. Perfil de Vulnerabilidade (Barras para melhor comparação)
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    resumo = contar_por_categoria()
    categorias = ['Grave', 'Moderada', 'Leve', 'Seguro']
    valores = [resumo.get(c, 0) for c in categorias]
    cores = ['#e53e3e', '#dd6b20', '#d69e2e', '#38a169']
    
    ax1.bar(categorias, valores, color=cores)
    ax1.set_title("Volume de Famílias por Nível de Risco")
    perfil_b64 = _plot_to_base64(fig1)

    # 2. Antecipação de Crises (Linhas: Chuva vs Vulnerabilidade)
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    datas, chuva_mm, alerta_familias = calcular_risco_enchente_vs_chuva()
    
    ax2.plot(datas, chuva_mm, color='blue', label='Chuva (mm)', marker='o')
    ax2.set_ylabel('Chuva (mm)', color='blue')
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))
    plt.xticks(rotation=45)
    
    ax2_twin = ax2.twinx()
    ax2_twin.plot(datas, alerta_familias, color='red', label='Alerta Estoque', linestyle='--')
    ax2_twin.set_ylabel('Famílias em Alerta', color='red')
    
    ax2.set_title("Monitoramento Sazonal para Estoque Emergencial")
    linhas_b64 = _plot_to_base64(fig2)

    # 3. Mapa de Calor com Identificação de Bairros
    lats, lngs, niveis = obter_dados_mapa_calor()
    mapa = folium.Map(location=[-2.5391, -44.2829], zoom_start=12, tiles='CartoDB positron')
    
    pesos = {'Grave': 1.0, 'Moderada': 0.7, 'Leve': 0.4, 'Seguro': 0.1}
    heat_data = [[lats[i], lngs[i], pesos.get(niveis[i], 0.1)] for i in range(len(lats))]
    HeatMap(heat_data, radius=15, blur=10).add_to(mapa)

    bairros_coords = carregar_bairros_coords()
    for b in bairros_coords:
        folium.CircleMarker(
            location=[b['latitude'], b['longitude']],
            radius=4, color='#2b6cb0', fill=True,
            tooltip=f"Bairro: <b>{b['nome']}</b>"
        ).add_to(mapa)

    mapa_html = mapa._repr_html_()

    # Construção do Dashboard Final
    html_content = f"""
    <html>
    <head><style>
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 20px; }}
        .row {{ display: flex; justify-content: space-around; margin-bottom: 20px; }}
        .card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    </style></head>
    <body>
        <h1 style="text-align:center;">🥗 Dashboard de Inteligência Alimentar - SLZ</h1>
        <div class="row">
            <div class="card"><img src="data:image/png;base64,{perfil_b64}"></div>
            <div class="card"><img src="data:image/png;base64,{linhas_b64}"></div>
        </div>
        <div class="card" style="width: 95%; margin: auto;">{mapa_html}</div>
    </body></html>"""
    
    with open("dashboard_slz.html", "w", encoding="utf-8") as f: f.write(html_content)
    print("Dashboard gerado com sucesso!")