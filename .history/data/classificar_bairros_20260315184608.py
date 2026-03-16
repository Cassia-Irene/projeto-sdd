import json

CLASSIFICACAO_TERRITORIAL = {
    # Nível 3 — Alta vulnerabilidade (Palafitas, ocupações, áreas rurais e periferias críticas)
    "Liberdade": 3, "Coroadinho": 3, "Camboa": 3, "Camboa dos Frades": 3,
    "Anjo da Guarda": 3, "Vila Embratel": 3, "Sá Viana": 3, "Gancharia": 3,
    "Vila Maranhão": 3, "Cajueiro": 3, "Cidade Olímpica": 3, "Vila Sarney": 3,
    "Vila Janaína": 3, "Santa Clara": 3, "Vila Cascavel": 3, "Santa Bárbara": 3,
    "Vila Itamar": 3, "Tajipuru": 3, "Coquilho": 3, "Mato Grosso": 3,
    "Quebra Pote": 3, "Recanto Verde": 3, "Recanto Canaã": 3, "Santa Helena": 3,
    "Vila Esperança": 3, "Coqueiro": 3, "Estiva": 3, "Itaqui": 3,
    "Ilhinha": 3, "Bacanga": 3, "Vila Nova": 3, "Vila São Luís": 3,
    "Vila Ariri": 3, "Pedrinhas": 3, "Fé em Deus": 3, "Jaracaty": 3,
    "Divineia": 3, "Vila Palmeira": 3, "Vila Luizão": 3, "Areinha": 3,
    "Gapara": 3, "Cidade Nova do Gapara": 3, "Rio dos Cachorros": 3,
    "Vila Nova República": 3, "Vila Romário": 3, "Cutim": 3, "Santa Rosa": 3,
    "Vila Samara": 3, "Vila Cutia": 3, "Vila Funil": 3, "Maracanã": 3,
    "Fumacê": 3, "Piancó": 3, "Vila Industrial": 3, "Tajaçuaba": 3,
    "Residencial 2000": 3, "Residencial Paraíso": 3, "Residencial Shalom": 3,
    "Residencial João do Vale": 3, "Vila Vitória": 3, "Bom Jesus": 3,
    # Inclui todos os "Residenciais" de programas sociais
    "Residencial Rio Anil": 3, "Residencial Primavera": 3, "Residencial Tiradentes": 3,
    "Residencial Santo Antônio": 3, "Residencial Ilha Bela": 3, "Residencial Amendoeira": 3,

    # Nível 2 — Periferia intermediária (Bairros consolidados, classe média-baixa/operária)
    "Turu": 2, "Habitacional Turu": 2, "Vinhais": 2, "Bequimão": 2,
    "Cohab Anil I": 2, "Cohab Anil II": 2, "Cohab Anil III": 2,
    "Cohab Anil IV": 2, "Cohab Anil V": 2, "Cohatrac I": 2, "Cohatrac II": 2,
    "Cohatrac III": 2, "Cohatrac IV": 2, "Cidade Operária": 2, "Forquilha": 2, 
    "São Bernardo": 2, "Ipase": 2, "Maranhão Novo": 2, "Angelim": 2, 
    "João Paulo": 2, "Monte Castelo": 2, "Alemanha": 2, "Anil": 2,
    "Bairro de Fátima": 2, "Fátima": 2, "Apeadouro": 2, "Ivar Saldanha": 2,
    "Caratatiua": 2, "Radional": 2, "Conjunto Radional": 2, "São Cristóvão": 2,
    "Vicente Fialho": 2, "Recanto dos Vinhais": 2, "Ipem Turu": 2,
    "Planalto Turu I": 2, "Planalto Turu II": 2, "Planalto Turu III": 2,
    "Jardim de Allah": 2, "Sol e Mar": 2, "Jardim Eldorado": 2,

    # Nível 1 — Bairros nobres/centrais (Baixa vulnerabilidade)
    "Calhau": 1, "Alto do Calhau": 1, "Ponta dAreia": 1, "São Marcos": 1,
    "Cohama": 1, "Olho dÁgua": 1, "Renascença": 1, "Jardim Renascença": 1,
    "Cohafuma": 1, "Cohajap": 1, "São Francisco": 1, "Jardim São Francisco": 1,
    "Ponta do Farol": 1, "Quintas do Calhau": 1, "Chácara Brasil": 1,
    "Parque Atenas": 1, "Parque Shalom": 1, "Recanto dos Nobres": 1
}

def enriquecer_bairros():
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)

    for b in bairros:
        b['vulnerabilidade_territorial'] = CLASSIFICACAO_TERRITORIAL.get(b['nome'], 2)

    with open('data/bairros_coords.json', 'w', encoding='utf-8') as f:
        json.dump(bairros, f, ensure_ascii=False, indent=4)

    atribuidos = sum(1 for b in bairros if b['nome'] in CLASSIFICACAO_TERRITORIAL)
    print(f"{len(bairros)} bairros enriquecidos ({atribuidos} com classificação explícita, {len(bairros) - atribuidos} com padrão 2).")


if __name__ == "__main__":
    enriquecer_bairros()