import requests
import json
import random
from faker import Faker

fake = Faker('pt_BR')
TOKEN = "de2273ac837e9af9d8a16a725cba72a0"
COD_IBGE_SLZ = "2111300" # Código de São Luís

# Probabilidades baseadas na Tabela 3
PROBABILIDADES = {
    "sem_agua": 0.31, "sem_banheiro": 0.57, "sem_lixo": 0.40, "analfabeto": 0.13
}

def buscar_beneficiarios_reais(quantidade=40):
    """Busca beneficiários reais do Bolsa Família em São Luís via API."""
    url = f"https://api.portaldatransparencia.gov.br/api-de-dados/bolsa-familia-por-municipio?codigoIbge={COD_IBGE_SLZ}&mesAno=202401&pagina=1"
    headers = {"chave-api-dados": TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            # Retorna apenas a lista de beneficiários limitada à quantidade desejada
            return dados[:quantidade]
    except Exception as e:
        print(f"Erro na API: {e}")
    return []

def classificar_inseguranca(renda, tem_privacao):
    if renda <= 0.3 and tem_privacao: return "Grave"
    elif renda <= 0.6: return "Moderada"
    elif renda <= 1.0: return "Leve"
    return "Seguro"

def gerar_familias(total_alvo=80):
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros_data = json.load(f)

    familias = {}
    contagem_bairros = {b['nome']: 0 for b in bairros_data}
    
    # 1. Busca os 40 nomes reais do Portal
    print(f"Acessando Portal da Transparência para buscar beneficiários de São Luís...")
    reais = buscar_beneficiarios_reais(quantidade=total_alvo//2)
    
    i = 0
    while i < total_alvo:
        # Seleção de bairro com trava de cota (máx 10 por bairro)
        bairro_obj = random.choice(bairros_data)
        nome_b = bairro_obj['nome']
        if contagem_bairros[nome_b] >= 10: continue

        # Lógica Híbrida
        if i < len(reais):
            # DADOS REAIS
            nome_responsavel = reais[i]['beneficiario']['nome']
            id_unico = f"NIS_{reais[i]['beneficiario']['nis']}"
            recebe_auxilio = True
        else:
            # DADOS FAKES
            nome_responsavel = fake.name()
            id_unico = fake.cpf()
            recebe_auxilio = False

        renda = round(random.uniform(0.0, 1.5), 2)
        s_banheiro = random.random() < PROBABILIDADES["sem_banheiro"] # Var 6
        s_agua = random.random() < PROBABILIDADES["sem_agua"]         # Var 5
        s_lixo = random.random() < PROBABILIDADES["sem_lixo"]         # Var 7
        
        privacao = s_banheiro or s_agua or s_lixo
        
        familias[id_unico] = {
            "responsavel": nome_responsavel,
            "bairro": nome_b,
            "latitude": bairro_obj['lat'],
            "longitude": bairro_obj['lng'],
            "renda_sm": renda,
            "sem_banheiro": s_banheiro,
            "sem_agua": s_agua,
            "sem_coleta": s_lixo,
            "analfabetismo": random.random() < PROBABILIDADES["analfabeto"], # Var 8
            "ja_recebe_auxilio": recebe_auxilio,
            "inseguranca": classificar_inseguranca(renda, privacao)
        }
        
        contagem_bairros[nome_b] += 1
        i += 1
    
    with open('data/familias_slz.json', 'w', encoding='utf-8') as f:
        json.dump(familias, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(reais)} nomes reais injetados. Total: {total_alvo} famílias.")

if __name__ == "__main__":
    gerar_familias()