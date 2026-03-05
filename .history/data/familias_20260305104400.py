import requests
import json
import random
from faker import Faker

fake = Faker('pt_BR')
# Coloque seu token aqui ou use uma variável de ambiente
TOKEN = "de2273ac837e9af9d8a16a725cba72a0" 

def consultar_portal(cpf_limpo):
    """Consulta se o CPF gerado já possui benefícios no Portal da Transparência"""
    url = f"https://api.portaldatransparencia.gov.br/api-de-dados/pessoa-fisica?cpf={cpf_limpo}"
    headers = {"chave-api-dados": TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def gerar_familias(quantidade=10): # Reduzi a quantidade para não estourar o limite da API (180/min)
    with open('data/bairros_slz.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)

    familias = {}
    
    for _ in range(quantidade):
        cpf_fake = fake.cpf()
        cpf_limpo = cpf_fake.replace('.', '').replace('-', '')
        
        # Tenta validar no portal
        dados_portal = consultar_portal(cpf_limpo)
        
        familias[cpf_fake] = {
            "responsavel": fake.name(),
            "bairro": random.choice(bairros),
            "renda_sm": round(random.uniform(0.0, 1.2), 2), # Var 9
            "sem_banheiro": random.choice([True, False]),     # Var 6
            "analfabetismo": random.choice([True, False]),    # Var 8
            "ja_recebe_auxilio": dados_portal['favorecidoNovoBolsaFamilia'] if dados_portal else False,
            "inseguranca": "Grave" if random.random() > 0.7 else "Moderada"
        }
    
    with open('data/familias_slz.json', 'w', encoding='utf-8') as f:
        json.dump(familias, f, ensure_ascii=False, indent=4)
    print(f"Sucesso! {quantidade} famílias geradas e validadas.")

if __name__ == "__main__":
    gerar_familias()