import requests
import json
import random
from faker import Faker

fake = Faker('pt_BR')
TOKEN = "de2273ac837e9af9d8a16a725cba72a0"
COD_IBGE_SLZ = "2111300"

# Probabilidades baseadas na Tabela 3
PROBABILIDADES = {
    "sem_agua": 0.31, "sem_banheiro": 0.57, "sem_lixo": 0.40, "analfabeto": 0.13
}

def buscar_beneficiarios_reais(quantidade=40):
    lista_final = []
    pagina_atual = 1

    headers = {"chave-api-dados": TOKEN}

    while len(lista_final) < quantidade_desejada:
        url = f"https://api.portaldatransparencia.gov.br/api-de-dados/novo-bolsa-familia-sacado-beneficiario-por-municipio?codigoIbge={COD_IBGE_SLZ}&mesAno=202401&pagina=1"
    
        try:
            print(f"🔍 Buscando dados... Página {pagina_atual}")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                dados = response.json()
                if not dados:
                    break
        except Exception as e:
            print(f"❌ Erro na API: {e}")
        return []

def classificar_inseguranca(renda, tem_privacao):
    if renda <= 0.3 and tem_privacao: return "Grave"
    elif renda <= 0.6: return "Moderada"
    elif renda <= 1.0: return "Leve"
    return "Seguro"

def gerar_familias(total_alvo=80):
    # Carrega coordenadas reais do dataset do Evanildo Barros
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros_data = json.load(f)

    familias = {}
    contagem_bairros = {b['nome']: 0 for b in bairros_data}
    
    print(f"🚀 Iniciando geração híbrida (Real + Fake)...")
    reais = buscar_beneficiarios_reais(quantidade=total_alvo//2)
    
    i = 0
    while i < total_alvo:
        # Seleção de bairro com controle de cota (máx 10 por bairro)
        bairro_obj = random.choice(bairros_data)
        nome_b = bairro_obj['nome']
        if contagem_bairros[nome_b] >= 10: continue

        # Lógica de Dados Reais vs Fakes
        if i < len(reais):
            # EXTRAÇÃO DO PORTAL (Dados Reais)
            beneficiario = reais[i]['beneficiarioNovoBolsaFamilia']
            nome_responsavel = beneficiario['nome']
            id_unico = f"NIS_{beneficiario['nis']}"
            recebe_auxilio = True
        else:
            # GERAÇÃO FAKE (Para quem não recebe auxílio)
            nome_responsavel = fake.name()
            id_unico = fake.cpf()
            recebe_auxilio = False

        # Variáveis socioeconômicas (Tabela 3)
        renda = round(random.uniform(0.0, 1.5), 2)
        s_banheiro = random.random() < PROBABILIDADES["sem_banheiro"]
        s_agua = random.random() < PROBABILIDADES["sem_agua"]
        s_lixo = random.random() < PROBABILIDADES["sem_lixo"]
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
            "analfabetismo": random.random() < PROBABILIDADES["analfabeto"],
            "ja_recebe_auxilio": recebe_auxilio,
            "inseguranca": classificar_inseguranca(renda, privacao)
        }
        
        contagem_bairros[nome_b] += 1
        i += 1
    
    # Salva o resultado final para ser usado pela lógica e dashboard
    with open('data/familias_slz.json', 'w', encoding='utf-8') as f:
        json.dump(familias, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Sucesso! {total_alvo} famílias geradas e salvas em /data/familias_slz.json")

if __name__ == "__main__":
    gerar_familias()