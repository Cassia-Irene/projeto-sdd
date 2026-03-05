import os
import json
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

def automatizar_extracao_pandas():
    print("Iniciando download e extração via Pandas...")
    file_path = "data_BR_MA_all.csv" 
    
    try:
        # 1. Corrigido para dataset_load (evitando o DeprecationWarning)
        df = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "itallonardi/bairros-povoados-e-distritos-do-brasil",
            file_path,
            pandas_kwargs={"sep": ",", "on_bad_lines": "skip", "encoding": "utf-8"}
        )
        
        df.columns = df.columns.str.lower()
        
        # 2. Mapeamento exato das colunas conforme o seu terminal!
        col_cidade = 'city'
        col_bairro = 'location_name'

        # 3. Filtra apenas a cidade de São Luís
        df_slz = df[df[col_cidade].astype(str).str.upper().isin(['SÃO LUÍS', 'SAO LUIS'])]
        
        # 4. Extrai a lista de bairros únicos da coluna 'location_name'
        bairros_unicos = df_slz[col_bairro].dropna().unique().tolist()
        bairros_limpos = sorted([str(b).strip() for b in bairros_unicos if str(b).strip()])
        
        # 5. Salva o Conjunto (Set) no formato JSON para o structures.py
        os.makedirs('data', exist_ok=True)
        caminho_json = os.path.join('data', 'bairros_slz.json')
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(bairros_limpos, f, ensure_ascii=False, indent=4)
            
        print(f"🎉 Sucesso total! {len(bairros_limpos)} bairros de São Luís extraídos e salvos em {caminho_json}")
        
        print("\nAmostra dos bairros salvos:")
        print(bairros_limpos[:5])

    except Exception as e:
        print(f"Erro durante o processamento com Pandas: {e}")

if __name__ == "__main__":
    automatizar_extracao_pandas()