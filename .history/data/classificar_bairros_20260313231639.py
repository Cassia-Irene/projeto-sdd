import json

QQErLv

def enriquecer_bairros():
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)

    for b in bairros:
        b['vulnerabilidade_territorial'] = CLASSIFICACAO_TERRITORIAL.get(b['nome'], 2)

    with open('data/bairros_coords.json', 'w', encoding='utf-8') as f:
        json.dump(bairros, f, ensure_ascii=False, indent=4)

    atribuidos = sum(1 for b in bairros if b['nome'] in CLASSIFICACAO_TERRITORIAL)
    print(f"✅ {len(bairros)} bairros enriquecidos ({atribuidos} com classificação explícita, {len(bairros) - atribuidos} com padrão 2).")


if __name__ == "__main__":
    enriquecer_bairros()