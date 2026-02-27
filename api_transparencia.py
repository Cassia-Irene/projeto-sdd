# api_transparencia.py
import requests

def obter_conjunto_assistidos():
    """
    Busca dados na API do Portal da Transparência e retorna um CONJUNTO (set)
    com os números de NIS das famílias que já recebem auxílio.
    """
    
    # Parâmetros para a busca
    codigo_ibge = "2111300" # São Luís
    mes_ano = "202401"      # Mês de referência (formato AAAAMM)
    pagina = 1              # Trazendo a página 1 (15 registros por página) para o teste
    
    # Endpoint que traz a lista de quem sacou o benefício no município
    url = f"https://api.portaldatransparencia.gov.br/api-de-dados/bolsa-familia-sacados-por-municipio?mesAno={mes_ano}&codigoIbge={codigo_ibge}&pagina={pagina}"
    
    # ATENÇÃO: Substitua pela chave gerada no site do Portal da Transparência
    headers = {
        "chave-api-dados": "COLOQUE_A_SUA_CHAVE_AQUI" 
    }
    
    # Criamos um Conjunto (Set) vazio para armazenar os NIS. 
    # Usar Set aqui é crucial para evitar NIS duplicados (estrutura de dados!)
    conjunto_nis_assistidos = set()
    
    print("Conectando à API do Portal da Transparência...")
    
    try:
        resposta = requests.get(url, headers=headers)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Percorre os dados devolvidos pela API
            for registro in dados:
                # Extrai o NIS do titular do benefício
                nis = registro['titularBolsaFamilia']['nis']
                
                # Adiciona o NIS ao nosso Conjunto
                conjunto_nis_assistidos.add(nis)
                
            print(f"Sucesso! {len(conjunto_nis_assistidos)} NIS de famílias assistidas foram carregados no Conjunto B.")
            return conjunto_nis_assistidos
            
        else:
            print(f"Erro na API. Código: {resposta.status_code}")
            # Retorna um conjunto com dados fictícios apenas para o código não quebrar caso a API caia na hora da apresentação
            return {"111", "333", "555"}
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return {"111", "333", "555"}

# Bloco de teste: Se você rodar apenas este arquivo, ele testa a função.
if __name__ == "__main__":
    nis_teste = obter_conjunto_assistidos()
    print(f"Amostra dos dados extraídos (Conjunto de Assistidos): {nis_teste}")