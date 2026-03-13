import os
import json
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

def automatizar_extracao_coordenadas():
    print("Iniciando extração de base geográfica de São Luís...")
    
    try:
        # 1. Carrega o dataset original
        df = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "evanildobarros/bairrosdesaoluis",
            "bairros4.csv",
        )
        
        df.columns = df.columns.str.lower()
        
        # 2. Mapeamento de colunas
        col_bairro = next((col for col in df.columns if 'bairro' in col or 'nome' in col), None)
        col_lat = next((col for col in df.columns if 'lat' in col), None)
        col_long = next((col for col in df.columns if 'long' in col), None)

        if not all([col_bairro, col_lat, col_long]):
            print("Erro: Colunas de coordenadas não encontradas no CSV.")
            return

        # 3. Cruzamento dinâmico com famílias para identificar bairros atendidos
        # Importante: O conjunto (Set) identifica quem já recebe auxílio
        caminho_familias = 'data/familias_slz.json'
        set_bairros_atendidos = set()
        
        if os.path.exists(caminho_familias):
            with open(caminho_familias, 'r', encoding='utf-8') as f:
                dados_familias = json.load(f)
                for f_id in dados_familias:
                    fam = dados_familias[f_id]
                    if fam.get('ja_recebe_auxilio'):
                        set_bairros_atendidos.add(fam.get('bairro'))
                        

        # 4. Estruturação simplificada (Base para o gerar_entregas.py)
        bairros_coords = []
        for _, linha in df.iterrows():
            nome_bairro = str(linha[col_bairro]).strip()
            
            bairros_coords.append({
                "nome": nome_bairro,
                "lat": float(linha[col_lat]),
                "lng": float(linha[col_long]),
                "atendido": nome_bairro in set_bairros_atendidos # Define o conjunto dinâmico
            })

        # 5. Persistência dos dados
        os.makedirs('data', exist_ok=True)
        caminho_json = os.path.join('data', 'bairros_coords.json')
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(bairros_coords, f, ensure_ascii=False, indent=4)
            
        print(f"🎉 Sucesso! {len(bairros_coords)} bairros mapeados.")
        print(f"📡 Conjunto de bairros atendidos atualizado: {len(set_bairros_atendidos)} bairros.")

    except Exception as e:
        print(f"❌ Erro ao processar coordenadas: {e}")

if __name__ == "__main__":
    automatizar_extracao_coordenadas()