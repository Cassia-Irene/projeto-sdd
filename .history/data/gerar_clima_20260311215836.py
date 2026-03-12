import requests
import json
import os

def coletar_dados_pluviometricos():
    print("☁️ Iniciando conexão com a API Open-Meteo para São Luís...")
    
    # Coordenadas centrais aproximadas de São Luís
    latitude = -2.53
    longitude = -44.30
    
    # Período de coleta (Início do ano até ontem)
    start_date = "2022-01-01"
    end_date = "2026-03-10"
    
    # Endpoint de dados históricos da Open-Meteo (Não precisa de Token!)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=America%2FSao_Paulo"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            dados_api = response.json()
            
            # A API devolve dois arrays paralelos: 'time' (datas) e 'precipitation_sum' (chuva em mm)
            datas = dados_api['daily']['time']
            chuvas = dados_api['daily']['precipitation_sum']
            
            # Vamos estruturar isso em uma lista de dicionários limpa
            historico_chuvas = []
            for i in range(len(datas)):
                # Proteção caso a API retorne 'null' para algum dia sem medição
                precipitacao = chuvas[i] if chuvas[i] is not None else 0.0
                historico_chuvas.append({
                    "data": datas[i],
                    "chuva_mm": precipitacao
                })
            
            # Garantindo que a pasta data/ existe e salvando o JSON
            os.makedirs('data', exist_ok=True)
            caminho_json = os.path.join('data', 'chuvas_slz.json')
            
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(historico_chuvas, f, ensure_ascii=False, indent=4)
                
            print(f"✅ Sucesso! Dados pluviométricos de {len(historico_chuvas)} dias coletados.")
            print(f"🌧️ Amostra das chuvas mais recentes: {historico_chuvas[-3:]}")
            
        else:
            print(f"⚠️ Erro na API Open-Meteo: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    coletar_dados_pluviometricos()