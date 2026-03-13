from faker import Faker
import json
import random

fake = Faker('pt_BR')

def gerar_familias(quantidade=50):
    # Carrega os bairros reais que você acabou de baixar
    with open('data/bairros_slz.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)

    familias = {}
    
    for _ in range(quantidade):
        cpf = fake.cpf()
        familias[cpf] = {
            "responsavel": fake.name(),
            "bairro": random.choice(bairros),
            "renda_sm": round(random.uniform(0.1, 1.5), 2), # Baseado na Var 9 da Tabela 3
            "sem_banheiro": random.choice([True, False]),     # Baseado na Var 6 da Tabela 3
            "membros": random.randint(1, 8),
            "inseguranca": random.choice(["Leve", "Moderada", "Grave"])
        }
    
    with open('data/familias_slz.json', 'w', encoding='utf-8') as f:
        json.dump(familias, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    gerar_familias()