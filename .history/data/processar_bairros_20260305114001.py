import os
import json
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

def automatizar_extracao_pandas():
    print("Iniciando download e carregamento do dataset via Pandas...")
    
    # Nome do arquivo focado no Maranhão dentro do dataset do Kaggle
    file_path = "data_BR_MA_all.csv" 
    
    try:
        # 1. Carrega o dataset diretamente para um DataFrame do Pandas
        # Usamos error_bad_lines/on_bad_lines para ignorar erros de formatação no CSV do Kaggle
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "itallonardi/bairros-povoados-e-distritos-do-brasil",
            file_path,
            pandas_kwargs={"sep": ",", "on_bad_lines": "skip", "encoding": "utf-8"}
        )
        
        # 2. Padroniza o nome de todas as colunas para minúsculas para não ter erro
        df.columns = df.columns.str.lower()
        
        print(f"Colunas encontradas no dataset: {df.columns.tolist()}")
        print("-" * 50)
        
        # 3. Identifica as colunas corretas dinamicamente (Datasets costumam variar o nome)
        col_cidade = next((col for col in df.columns if col in ['municipio', 'cidade', 'name_muni', 'nm_mun']), None)
        col_bairro = next((col for col in df.columns if col in ['bairro', 'nome', 'name_neighborhood', 'nm_bairro']), None)
        
        if not col_cidade or not col_bairro:
            print("Erro: Não foi possível identificar as colunas de cidade ou bairro no CSV.")
            return

        # 4. Filtra apenas a cidade de São Luís (converte para maiúsculo para evitar problemas com acentos)
        df_slz = df[df[col_cidade].astype(str).str.upper().isin(['SÃO LUÍS', 'SAO LUIS'])]
        
        # 5. Extrai a lista de bairros únicos (dropando valores nulos)
        bairros_unicos = df_slz[col_bairro].dropna().unique().tolist()
        
        # Limpa espaços em branco e garante que está em ordem alfabética
        bairros_limpos = sorted([str(b).strip() for b in bairros_unicos if str(b).strip()])
        
        # 6. Salva o Conjunto (Set) no formato JSON para o structures.py
        os.makedirs('data', exist_ok=True)
        caminho_json = os.path.join('data', 'bairros_slz.json')
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(bairros_limpos, f, ensure_ascii=False, indent=4)
            
        print(f"🎉 Sucesso total! {len(bairros_limpos)} bairros extraídos e salvos em {caminho_json}")
        
        # Opcional: Mostra os primeiros registros para você ter certeza que deu certo
        print("\nAmostra dos bairros salvos:")
        print(bairros_limpos[:5])

    except Exception as e:
        print(f"Erro durante o processamento com Pandas: {e}")
        print("\nDica: Se o erro for de separador, altere sep=',' para sep=';' nos pandas_kwargs.")

if __name__ == "__main__":
    automatizar_extracao_pandas()