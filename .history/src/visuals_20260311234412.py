import matplotlib.pyplot as plt
from src.logic import contar_por_categoria, calcular_risco_enchente_vs_chuva, obter_dados_mapa_calor

def gerar_dashboard_html():
    """
    Gera um Dashboard visual integrado com os dados do Ecossistema Alimentar.
    """
    # Cria a figura principal do Dashboard com tamanho ajustado
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle('Ecossistema de Inteligência Alimentar - Painel de Controlo', fontsize=18, fontweight='bold')

    # ==========================================
    # 1. GRÁFICO DE PIZZA (Perfil das Famílias)
    # ==========================================
    ax1 = fig.add_subplot(2, 2, 1) # Linha 1, Coluna 1
    resumo = contar_por_categoria()
    
    # Filtra apenas as categorias que têm valores maiores que 0
    labels = [k for k, v in resumo.items() if v > 0]
    sizes = [v for v in resumo.values() if v > 0]
    
    # Define as cores para cada nível de vulnerabilidade
    cores_dict = {'Grave': '#ff9999', 'Moderada': '#ffcc99', 'Leve': '#ffff99', 'Seguro': '#99ff99'}
    cores_pizza = [cores_dict.get(l, '#cccccc') for l in labels]
    
    ax1.pie(sizes, labels=labels, colors=cores_pizza, autopct='%1.1f%%', startangle=140, shadow=True)
    ax1.set_title("Perfil das Famílias Atendidas")

    # ==========================================
    # 2. GRÁFICO DE LINHAS (Enchentes vs Estoque)
    # ==========================================
    ax2 = fig.add_subplot(2, 2, 2) # Linha 1, Coluna 2
    datas, chuva_mm, alerta_familias = calcular_risco_enchente_vs_chuva()
    
    # Eixo principal (Chuva)
    ax2.plot(datas, chuva_mm, color='blue', label='Chuva (mm)', marker='o', linewidth=2)
    ax2.set_ylabel('Precipitação (mm)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.tick_params(axis='x', rotation=45) # Roda as datas para facilitar a leitura
    
    # Eixo secundário partilhado (Famílias em Alerta)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(datas, alerta_familias, color='red', label='Famílias em Risco (Alerta > 15mm)', linestyle='--', marker='x')
    ax2_twin.set_ylabel('Nº Famílias Vulneráveis', color='red')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    
    ax2.set_title("Previsão: Chuvas vs Necessidade de Estoque")
    ax2.grid(True, linestyle=':', alpha=0.6)

    # ==========================================
    # 3. MAPA DE CALOR ESPACIAL (Heatmap)
    # ==========================================
    ax3 = fig.add_subplot(2, 1, 2) # Linha 2, ocupa a largura inteira
    lats, lngs, niveis = obter_dados_mapa_calor()
    
    # Mapeia os níveis de risco para cores no gráfico de dispersão
    cores_mapa = {'Grave': 'red', 'Moderada': 'orange', 'Leve': 'yellow', 'Seguro': 'green'}
    cores_pontos = [cores_mapa.get(n, 'blue') for n in niveis]
    
    # Cria o gráfico de dispersão (scatter) simulando o mapa de calor
    ax3.scatter(lngs, lats, c=cores_pontos, alpha=0.7, s=150, edgecolors='black')
    ax3.set_title("Heatmap: Localização Crítica de Insegurança Alimentar")
    ax3.set_xlabel("Longitude")
    ax3.set_ylabel("Latitude")
    ax3.grid(True, linestyle='--', alpha=0.5)

    # ==========================================
    # RENDERIZAÇÃO
    # ==========================================
    plt.tight_layout() # Ajusta os espaços para não sobrepor textos
    plt.subplots_adjust(top=0.90) # Dá espaço para o título principal
    plt.show() # Exibe o ecrã com o Dashboard