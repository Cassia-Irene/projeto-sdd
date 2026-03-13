import os
import json
from src.logic import contar_por_categoria, calcular_risco_enchente_vs_chuva

def gerar_dashboard_html():
    print("🎨 Iniciando geração do Dashboard HTML...")
    
    # Busca os dados calculados pelo logic.py
    perfil = contar_por_categoria()
    datas, chuva_mm, alertas = calcular_risco_enchente_vs_chuva()
    
    # Formata as listas do Python para o formato que o JavaScript do Chart.js entende (JSON strings)
    labels_pizza = json.dumps(list(perfil.keys()))
    dados_pizza = json.dumps(list(perfil.values()))
    
    labels_linha = json.dumps(datas)
    dados_chuva = json.dumps(chuva_mm)
    dados_alerta = json.dumps(alertas)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ecossistema Inteligente - SLZ</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{ --bg: #f8f9fa; --card-bg: #ffffff; --text: #2c3e50; --accent: #3498db; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .header h1 {{ margin: 0; color: var(--accent); }}
            .grid {{ display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }}
            .card {{ background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .chart-container {{ position: relative; height: 300px; width: 100%; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Painel de Inteligência Alimentar - São Luís</h1>
                <p>Monitoramento de Insegurança Familiar e Prevenção de Desastres (Quadra Chuvosa 2026)</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>Perfil de Insegurança (80 Famílias)</h3>
                    <div class="chart-container">
                        <canvas id="pizzaChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <h3>Impacto Climático nas Áreas Vulneráveis</h3>
                    <div class="chart-container">
                        <canvas id="linhaChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // 1. Configuração do Gráfico de Pizza (Perfil)
            const ctxPizza = document.getElementById('pizzaChart').getContext('2d');
            new Chart(ctxPizza, {{
                type: 'doughnut',
                data: {{
                    labels: {labels_pizza},
                    datasets: [{{
                        data: {dados_pizza},
                        backgroundColor: ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71'], // Grave, Moderada, Leve, Seguro
                        borderWidth: 2
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});

            // 2. Configuração do Gráfico de Linhas (Chuva x Alerta)
            const ctxLinha = document.getElementById('linhaChart').getContext('2d');
            new Chart(ctxLinha, {{
                type: 'line',
                data: {{
                    labels: {labels_linha},
                    datasets: [
                        {{
                            label: 'Chuva Diária (mm)',
                            data: {dados_chuva},
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.2)',
                            yAxisID: 'y',
                            fill: true,
                            tension: 0.3
                        }},
                        {{
                            type: 'bar',
                            label: 'Pico de Risco (Famílias Afetadas)',
                            data: {dados_alerta},
                            backgroundColor: 'rgba(231, 76, 60, 0.6)',
                            yAxisID: 'y1'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ type: 'linear', display: true, position: 'left', title: {{display: true, text: 'Chuva (mm)'}} }},
                        y1: {{ type: 'linear', display: true, position: 'right', title: {{display: true, text: 'Famílias em Risco'}}, grid: {{drawOnChartArea: false}} }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    caminho_html = os.path.join(os.getcwd(), 'dashboard_slz.html')
    with open(caminho_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"✨ Concluído! Arquivo gerado em: {caminho_html}")
    print("👉 Abra este arquivo no seu navegador (Chrome/Edge) para visualizar.")

if __name__ == "__main__":
    gerar_dashboard_html()