import requests
import json
import random
from faker import Faker

fake = Faker('pt_BR')
TOKEN = "de2273ac837e9af9d8a16a725cba72a0" 

# Médias baseadas na Tabela 3
PROBABILIDADES = {
    "sem_agua": 0.31,
    "sem_banheiro": 0.57,
    "sem_lixo": 0.40,
    "analfabeto": 0.13
}

def consultar_portal(cpf_limpo):
    url = f"https://api.portaldatransparencia.gov.br/api-de-dados/pessoa-fisica?cpf={cpf_limpo}"
    headers = {"chave-api-dados": TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def classificar_inseguranca(renda, tem_privacao):
    """Define o nível de insegurança baseado na Renda (Var 9) e Infraestrutura."""
    if renda <= 0.3 and tem_privacao:
        return "Grave"
    elif renda <= 0.6:
        return "Moderada"
    elif renda <= 1.0:
        return "Leve"
    else:
        return "Seguro"

def gerar_familias(quantidade=80):
    # Carrega os bairros com coordenadas
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros_data = json.load(f)

    familias = {}
    # Dicionário para controlar a cota: cada bairro pode aparecer no máximo 10 vezes
    contagem_bairros = {b['nome']: 0 for b in bairros_data}
    
    i = 0
    while i < quantidade:
        bairro_obj = random.choice(bairros_data)
        nome_b = bairro_obj['nome']
        
        # Só prossegue se o bairro ainda não atingiu a cota de 10
        if contagem_bairros[nome_b] >= 10:
            continue
            
        cpf_fake = fake.cpf()
        cpf_limpo = cpf_fake.replace('.', '').replace('-', '')
        dados_portal = consultar_portal(cpf_limpo)
        
        # Geração de variáveis da Tabela 3
        renda = round(random.uniform(0.0, 1.5), 2)
        s_banheiro = random.random() < PROBABILIDADES["sem_banheiro"]
        s_agua = random.random() < PROBABILIDADES["sem_agua"]
        s_lixo = random.random() < PROBABILIDADES["sem_lixo"]
        
        privacao = s_banheiro or s_agua or s_lixo
        
        familias[cpf_fake] = {
            "responsavel": fake.name(),
            "bairro": nome_b,
            "latitude": bairro_obj['lat'],
            "longitude": bairro_obj['lng'],
            "renda_sm": renda,
            "sem_banheiro": s_banheiro,
            "sem_agua": s_agua,
            "sem_coleta": s_lixo,
            "analfabetismo": random.random() < PROBABILIDADES["analfabeto"],
            "ja_recebe_auxilio": dados_portal['favorecidoNovoBolsaFamilia'] if dados_portal else False,
            "inseguranca": classificar_inseguranca(renda, privacao)
        }
        
        contagem_bairros[nome_b] += 1
        i += 1
    
    with open('data/familias_slz.json', 'w', encoding='utf-8') as f:
        json.dump(familias, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {quantidade} famílias geradas com distribuição equilibrada por bairro.")

if __name__ == "__main__":
    gerar_familias()