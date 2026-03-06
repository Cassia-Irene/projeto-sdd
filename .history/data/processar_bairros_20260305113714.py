import kagglehub
import csv
import json
import os
import glob


def automatizar_extracao_bairros():
    print("Iniciando download do dataset do Kaggle...")
    
    # 1. Faz o download do dataset usando a biblioteca oficial do Kaggle
    caminho_dataset = kagglehub.dataset_download("itallonardi/bairros-povoados-e-distritos-do-brasil")
    print(f"Dataset baixado temporariamente em: {caminho_dataset}")
    
    # 2. Encontra o arquivo específico do Maranhão (MA) dentro da pasta baixada
    arquivos_csv = glob.glob(os.path.join(caminho_dataset, "*MA*.csv"))
    
    if not arquivos_csv:
        # Fallback caso o nome do arquivo seja diferente, pega o primeiro CSV que achar
        arquivos_csv = glob.glob(os.path.join(caminho_dataset, "*.csv"))
        
    if not arquivos_csv:
        print("Erro: Nenhum arquivo CSV encontrado no dataset.")
        return

    caminho_csv = arquivos_csv[0]
    print(f"Processando o arquivo: {caminho_csv}")
    
    bairros_slz = set()

    # 3. Lê o CSV e filtra os bairros de São Luís
    try:
        with open(caminho_csv, mode='r', encoding='utf-8') as f:
            leitor = csv.DictReader(f)
            
            for linha in leitor:
                # Transforma as chaves em minúsculas para evitar erros de digitação do CSV
                linha_lower = {k.lower(): v for k, v in linha.items()}
                
                # Pega as colunas de cidade e bairro (ajustando para os nomes mais comuns em datasets)
                cidade = str(linha_lower.get('municipio', linha_lower.get('cidade', ''))).strip().upper()
                
                if cidade in ['SÃO LUÍS', 'SAO LUIS']:
                    bairro = str(linha_lower.get('bairro', linha_lower.get('nome', ''))).strip()
                    if bairro:
                        bairros_slz.add(bairro)

        # 4. Salva o Conjunto (Set) no seu arquivo JSON local
        os.makedirs('data', exist_ok=True) # Garante que a pasta /data existe
        caminho_json = os.path.join('data', 'bairros_slz.json')
        
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(sorted(list(bairros_slz)), f, ensure_ascii=False, indent=4)
            
        print(f"🎉 Sucesso total! {len(bairros_slz)} bairros de São Luís extraídos e salvos em {caminho_json}")

    except Exception as e:
        print(f"Erro durante o processamento: {e}")

if __name__ == "__main__":
    automatizar_extracao_bairros()