CLASSIFICACAO_TERRITORIAL = {
    # Nível 3 — Alta vulnerabilidade (palafitas, favelas, ocupações)
    "Liberdade": 3, "Coroadinho": 3, "Camboa": 3, "Camboa dos Frades": 3,
    "Anjo da Guarda": 3, "Vila Embratel": 3, "Sá Viana": 3, "Gancharia": 3,
    "Vila Maranhão": 3, "Cajueiro": 3, "Cidade Olímpica": 3, "Vila Sarney": 3,
    "Vila Janaína": 3, "Santa Clara": 3, "Vila Cascavel": 3, "Santa Bárbara": 3,
    "Vila Itamar": 3, "Tajipuru": 3, "Coquilho": 3, "Mato Grosso": 3,
    "Quebra Pote": 3, "Recanto Verde": 3, "Recanto Canaã": 3, "Santa Helena": 3,
    "Vila Esperança": 3, "Coqueiro": 3, "Estiva": 3, "Itaqui": 3,
    "Ilhinha": 3, "Bacanga": 3, "Vila Nova": 3, "Vila São Luís": 3,
    "Vila Ariri": 3, "Pedrinhas": 3, "Fé em Deus": 3,

    # Nível 2 — Periferia intermediária (carências, sem palafitas típicas)
    "Turu": 2, "Habitacional Turu": 2, "Vinhais": 2, "Bequimão": 2,
    "Cohab Anil I": 2, "Cohab Anil II": 2, "Cohab Anil III": 2,
    "Cohab Anil IV": 2, "Cohab Anil V": 2, "Cohatrac I": 2, "Cohatrac II": 2,
    "Cohatrac III": 2, "Cohatrac IV": 2, "Cidade Operária": 2,
    "Forquilha": 2, "São Bernardo": 2, "Ipase": 2, "Maranhão Novo": 2,

    # Nível 1 — Bairros nobres/centrais
    "Calhau": 1, "Alto do Calhau": 1, "Ponta d'Areia": 1, "São Marcos": 1,
    "Cohama": 1, "Olho d'Água": 1, "Renascença": 1, "Jardim Renascença": 1,
    "Cohafuma": 1, "Cohajap": 1, "São Francisco": 1, "Jardim São Francisco": 1,
}

def enriquecer_bairros():
    import json
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)
    
    for b in bairros:
        b['vulnerabilidade_territorial'] = CLASSIFICACAO_TERRITORIAL.get(b['nome'], 2)
    
    with open('data/bairros_coords.json', 'w', encoding='utf-8') as f:
        json.dump(bairros, f, ensure_ascii=False, indent=4)
    
    print("✅ Bairros enriquecidos com classificação territorial.")