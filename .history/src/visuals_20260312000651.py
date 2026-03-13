import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import folium
from folium.plugins import HeatMap
import io
import base64
import os
from src.logic import contar_por_categoria, calcular_risco_enchente_vs_chuva, obter_dados_mapa_calor

# 👇 IMPORT NOVO AQUI: Trazendo a função que carrega as coordenadas dos bairros
from src.structures import carregar_bairros_coords 

def _plot_to_base64(fig):
    """Função auxiliar para converter o gráfico Matplotlib numa imagem embutida pro HTML"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close(fig) # Fecha a figura para poupar memória
    return base64.b64encode(buf.read()).decode('utf-8')

def gerar_dashboard_html():
    """
    Gera um Dashboard HTML com gráficos Matplotlib e um mapa real do Folium.
    """
    print("Gerando gráficos...")
    
    # ==========================================
    # 1. GRÁFICO DE PIZZA (Perfil das Famílias)
    # ==========================================
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    resumo = contar_por_categoria()
    labels = [k for k, v in resumo.items() if v > 0]
    sizes = [v for v in resumo.values() if v > 0]
    cores_dict = {'Grave': '#ff9999', 'Moderada': '#ffcc99', 'Leve': '#ffff99', 'Seguro': '#99ff99'}
    cores_pizza = [cores_dict.get(l, '#cccccc') for l in labels]
    ax1.pie(sizes, labels=labels, colors=cores_pizza, autopct='%1.1f%%', startangle=140, shadow=True)
    ax1.set_title("Perfil das Famílias Atendidas")
    pizza_b64 = _plot_to_base64(fig1)

    # ==========================================
    # 2. GRÁFICO DE LINHAS (Arrumado para não borrar)
    # ==========================================
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    datas, chuva_mm, alerta_familias = calcular_risco_enchente_vs_chuva()
    
    ax2.plot(datas, chuva_mm, color='blue', label='Chuva (mm)', marker='o', linewidth=2)
    ax2.set_ylabel('Precipitação (mm)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    ax2.tick_params(axis='x', rotation=45)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(5)) 
    
    ax2_twin = ax2.twinx()
    ax2_twin.plot(datas, alerta_familias, color='red', label='Famílias Risco', linestyle='--', marker='x')
    ax2_twin.set_ylabel('Nº Famílias Vulneráveis', color='red')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    
    ax2.set_title("Previsão: Chuvas vs Necessidade de Estoque")
    ax2.grid(True, linestyle=':', alpha=0.6)
    linhas_b64 = _plot_to_base64(fig2)

    # ==========================================
    # 3. MAPA DO FOLIUM (Heatmap + Marcadores de Bairros)
    # ==========================================
    print("Gerando mapa espacial de São Luís...")
    lats, lngs, niveis = obter_dados_mapa_calor()
    
    mapa = folium.Map(location=[-2.5391, -44.2829], zoom_start=12, tiles='CartoDB positron')
    
    pesos = {'Grave': 1.0, 'Moderada': 0.7, 'Leve': 0.4, 'Seguro': 0.1}
    heat_data = [[lats[i], lngs[i], pesos.get(niveis[i], 0.1)] for i in range(len(lats))]
    HeatMap(heat_data, radius=15, blur=10).add_to(mapa)

    # 👇 CÓDIGO NOVO: ADICIONANDO MARCADORES DOS BAIRROS
    bairros_dados = carregar_bairros_coords()
    for bairro in bairros_dados:
        # Pega as coordenadas (usando .get de forma segura)
        lat = bairro.get('latitude') or bairro.get('lat')
        lng = bairro.get('longitude') or bairro.get('lng') or bairro.get('lon')
        nome = bairro.get('nome')
        
        if lat and lng and nome:
            # Adiciona um marcador de círculo sutil
            folium.CircleMarker(
                location=[lat, lng],
                radius=4,
                color='#2b6cb0', # Azul escuro
                fill=True,
                fill_opacity=0.9,
                tooltip=f"📍 Bairro: <b>{nome}</b>" # Balão que aparece ao passar o mouse!
            ).add_to(mapa)
    # 👆 FIM DO CÓDIGO NOVO

    mapa_html = mapa._repr_html_()

    # ==========================================
    # 4. CONSTRUÇÃO DO ARQUIVO HTML FINAL
    # ==========================================
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard - Inteligência Alimentar</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; color: #333; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #1a365d; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 15px; }}
            .map-container {{ width: 90%; max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 15px; }}
        </style>
    </head>
    <body>
        <h1>🥗 Ecossistema de Inteligência Alimentar - São Luís/MA</h1>
        
        <div class="container">
            <div class="card">
                <img src="data:image/png;base64,{pizza_b64}" alt="Gráfico de Pizza">
            </div>
            <div class="card">
                <img src="data:image/png;base64,{linhas_b64}" alt="Gráfico de Linhas">
            </div>
        </div>

        <div class="map-container">
            <h2 style="text-align: center; color: #2d3748; margin-top: 0;">Mapa de Calor de Vulnerabilidade (Tempo Real)</h2>
            {mapa_html}
        </div>
    </body>
    </html>
    """
    
    caminho_arquivo = os.path.abspath("dashboard_slz.html")
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n✅ SUCESSO! Dashboard gerado.")
    print(f"👉 Dê um clique duplo ou abra este arquivo no seu navegador: {caminho_arquivo}")