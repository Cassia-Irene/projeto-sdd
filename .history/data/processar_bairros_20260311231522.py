import os
import json
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

def automatizar_extracao_coordenadas():
    print("Iniciando download do dataset de coordenadas de São Luís...")
    
    try:
        # 1. Carrega o dataset 
        df = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "evanildobarros/bairrosdesaoluis",
            "bairros4.csv",
        )
        
        df.columns = df.columns.str.lower()
        print(f"Colunas detectadas: {df.columns.tolist()}")

        # 2. Identifica colunas de Bairro, Lat e Long
    
        col_bairro = next((col for col in df.columns if 'bairro' in col or 'nome' in col), None)
        col_lat = next((col for col in df.columns if 'lat' in col), None)
        col_long = next((col for col in df.columns if 'long' in col), None)

        if not all([col_bairro, col_lat, col_long]):
            print("Erro: Não foi possível mapear colunas de coordenadas.")
            return

        bairros_coords = []
        for _, linha in df.iterrows():
            bairros_coords.append({
                "nome": str(linha[col_bairro]).strip(),
                "lat": float(linha[col_lat]),
                "lng": float(linha[col_long])
            })

        # 4. Salva no JSON
        os.makedirs('data', exist_ok=True)
        caminho_json = os.path.join('data', 'bairros_coords.json')
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(bairros_coords, f, ensure_ascii=False, indent=4)
            
        print(f"🎉 Sucesso! {len(bairros_coords)} bairros com coordenadas salvos em {caminho_json}")

    except Exception as e:
        print(f"Erro ao processar coordenadas: {e}")

if __name__ == "__main__":
    automatizar_extracao_coordenadas()