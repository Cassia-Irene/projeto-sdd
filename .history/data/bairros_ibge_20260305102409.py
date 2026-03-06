import requests
import json

def baixar_dados_ibge():
    """
    Consome a API de Localidades do IBGE para buscar os distritos de São Luís.
    Gera o arquivo bairros_slz.json para uso no sistema.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/2111300/distritos"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        
        # Extrai apenas os nomes para facilitar o uso em (Sets) 
        nomes_bairros = [item['nome'] for item in dados]
        
        # Salva em JSON
        with open('data/bairros_slz.json', 'w', encoding='utf-8') as f:
            json.dump(nomes_bairros, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso! {len(nomes_bairros)} bairros salvos em /data/bairros_slz.json")
    except Exception as e:
        print(f"Erro ao baixar dados: {e}")

if __name__ == "__main__":
    baixar_dados_ibge()