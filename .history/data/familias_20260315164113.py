import requests
import json
import random
from faker import Faker

fake = Faker('pt_BR')
TOKEN = "de2273ac837e9af9d8a16a725cba72a0"
COD_IBGE_SLZ = "2111300"

# ── Probabilidades calibradas pelo MIANMA/SEDES 2024/25 ──────────────────────
# Fonte: Diagnóstico da Insegurança Alimentar e Nutricional — Região da Ilha
# do Maranhão, Secretaria de Estado do Desenvolvimento Social, outubro 2025.
#
# tem_menor_18      → 30,03% dos domicílios tinham menores de 18 anos.
#                     Domicílios com menores: IG grave 10,31% vs 3,56% (Tab. 6)
#
# escolaridade_baixa → sem escolaridade + ensino fundamental = 49% da amostra.
#                     IG grave sobe a 14,29% entre analfabetos (Tab. 9)
#
# raca_preta        → 33,04% autodeclarados pretos. Apenas 31,51% desse grupo
#                     em segurança alimentar vs 50% pardos/brancos (Tab. 7)
#
# doenca_recente    → 31,09% reportaram doença nos 3 meses anteriores.
#                     Correlacionado com insegurança moderada/grave (Tab. 12)
#
# saude_mental      → 21,65% relataram depressão, ansiedade ou pânico.
#                     Só 21,43% desses estão em segurança alimentar (Tab. 14)
PROBABILIDADES = {
    "tem_menor_18": 0.30,
    "escolaridade_baixa": 0.49,
    "raca_preta": 0.33,
    "doenca_recente": 0.31,
    "saude_mental": 0.22,
    "moradia_precaria": 0.15  
}

# Tamanho domiciliar

# Categoria Habitacional
MORADIAS_POR_TERRITORIO = {
    1: [
        ("Apartamento (Privado)", 0.45, 0),
        ("Alvenaria (Regular)",   0.45, 0),
        ("Conjunto Habitacional", 0.10, 0),
    ],
    2: [
        ("Apartamento (Privado)", 0.10, 0),
        ("Alvenaria (Regular)",   0.50, 0),
        ("Conjunto Habitacional", 0.20, 0),
        ("Casa de Madeira",       0.15, 1),
        ("Taipa/Barro",           0.05, 2),
    ],
    3: [
        ("Apartamento (Privado)", 0.02, 0),
        ("Alvenaria (Regular)",   0.35, 0),
        ("Conjunto Habitacional", 0.10, 0),
        ("Casa de Madeira",       0.23, 1),
        ("Taipa/Barro",           0.20, 2),
        ("Palafita",              0.10, 4),
    ],
}

# ── Distribuição de renda alinhada ao perfil real de São Luís ─────────────────
# SEDES: 39% até 1SM · 34,65% de 1–3SM · 16,23% de 3–5SM · 10,09% acima de 5
FAIXAS_RENDA_POR_TERRITORIO = {
    1: [
        (1.50, 3.00, 0.20),
        (3.00, 5.00, 0.40),
        (5.00, 8.00, 0.40),
    ],
    2: [
        (0.00, 1.00, 0.39),
        (1.00, 3.00, 0.35),
        (3.00, 5.00, 0.16),
        (5.00, 8.00, 0.10),
    ],
    3: [
        (0.00, 0.50, 0.35),
        (0.50, 1.00, 0.30),
        (1.00, 3.00, 0.25),
        (3.00, 5.00, 0.10),
    ],
}

def _sortear_moradia_por_territorio(vuln_territorial: int):
    opcoes = MORADIAS_POR_TERRITORIO.get(vuln_territorial, MORADIAS_POR_TERRITORIO[2])
    r = random.random()
    acumulado = 0.0
    for tipo, peso, pontos in opcoes:
        acumulado += peso
        if r <= acumulado:
            return tipo, pontos
    # Fallback seguro: último item da lista
    return opcoes[-1][0], opcoes[-1][2]

def _sortear_renda_por_territorio(vuln_territorial: int) -> float:
    """Sorteia renda respeitando as faixas do diagnóstico SEDES."""
    faixas = FAIXAS_RENDA_POR_TERRITORIO.get(vuln_territorial, FAIXAS_RENDA_POR_TERRITORIO[2])
    r = random.random()
    acumulado = 0.0
    for minimo, maximo, peso in faixas:
        acumulado += peso
        if r <= acumulado:
            return round(random.uniform(minimo, maximo), 2)
    # Fallback: topo da última faixa disponível
    ultimo_max = faixas[-1][1]
    return round(random.uniform(faixas[-1][0], ultimo_max), 2)


def classificar_inseguranca(renda, tem_menor, escolaridade_baixa, pts_moradia, vulnerabilidade_territorial=2):
    """
    Classifica o nível de insegurança alimentar com base em três fatores
    validados pelo diagnóstico MIANMA/SEDES 2024/25 para a Ilha do Maranhão.

    Sistema de pontuação:
      Renda <= 0.3 SM    → +3 pts  (11,24% IG grave nessa faixa, Tab. 8)
      Renda <= 1.0 SM    → +1 pt   (faixa vulnerável, Tab. 8)
      Tem menor de 18    → +2 pts  (IG grave 10,31% vs 3,56%, Tab. 6)
      Escolaridade baixa → +1 pt   (IG grave até 14,29%, Tab. 9)

    Resultado:
      score >= 5 → Grave
      score >= 3 → Moderada
      score >= 1 → Leve
      score  = 0 → Seguro
    """
    score = 0

    if renda <= 0.3:
        score += 3
    elif renda <= 1.0:
        score += 1

    if tem_menor:
        score += 2

    if escolaridade_baixa:
        score += 1

    score += pts_moradia

    if vulnerabilidade_territorial == 3:
        score += 2
    elif vulnerabilidade_territorial == 2:
        score += 1

    if score >= 7:   return "Grave"
    elif score >= 5: return "Moderada"
    elif score >= 2: return "Leve"
    return "Seguro"


def buscar_beneficiarios_reais(quantidade=40):
    lista_final = []
    pagina_atual = 1
    headers = {"chave-api-dados": TOKEN}

    while len(lista_final) < quantidade:
        url = (
            f"https://api.portaldatransparencia.gov.br/api-de-dados/"
            f"novo-bolsa-familia-sacado-beneficiario-por-municipio"
            f"?codigoIbge={COD_IBGE_SLZ}&mesAno=202401&pagina={pagina_atual}"
        )
        try:
            print(f"🔍 Buscando dados... Página {pagina_atual}")
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                dados = response.json()
                if not dados:
                    break
                lista_final.extend(dados)
                pagina_atual += 1
            else:
                print(f"Erro na página {pagina_atual}: Status {response.status_code}")
                break

        except Exception as e:
            print(f"Erro na API: {e}")
            break

    print(f"Total de beneficiários reais coletados: {len(lista_final[:quantidade])}")
    return lista_final[:quantidade]


def gerar_familias(total_alvo=80):
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros_data = json.load(f)

    familias = {}
    contagem_bairros = {b['nome']: 0 for b in bairros_data}

    print("Iniciando geração híbrida...")
    reais = buscar_beneficiarios_reais(quantidade=total_alvo // 2)

    i = 0
    while i < total_alvo:
        bairro_obj = random.choice(bairros_data)
        nome_b = bairro_obj['nome']
        if contagem_bairros[nome_b] >= 10:
            continue

        vuln_territorial = bairro_obj.get('vulnerabilidade_territorial', 2)

        # ── Identidade ────────────────────────────────────────────────────────
        if i < len(reais):
            beneficiario     = reais[i]['beneficiarioNovoBolsaFamilia']
            nome_responsavel = beneficiario['nome']
            id_unico         = f"NIS_{beneficiario['nis']}"
            recebe_auxilio   = True
        else:
            nome_responsavel = fake.name()
            id_unico         = fake.cpf()
            recebe_auxilio   = False

        # ── Variáveis socioeconômicas (calibradas pela SEDES) ─────────────────
        renda              = _sortear_renda_por_territorio(vuln_territorial)
        tem_menor          = random.random() < PROBABILIDADES["tem_menor_18"]
        escolaridade_baixa = random.random() < PROBABILIDADES["escolaridade_baixa"]
        raca_preta         = random.random() < PROBABILIDADES["raca_preta"]
        doenca_recente     = random.random() < PROBABILIDADES["doenca_recente"]
        saude_mental       = random.random() < PROBABILIDADES["saude_mental"]
        tipo_casa, pts_casa = tipo_casa, pts_casa = _sortear_moradia_por_territorio(vuln_territorial)
        

        familias[id_unico] = {
            "responsavel":        nome_responsavel,
            "bairro":             nome_b,
            "latitude":           bairro_obj['lat'],
            "longitude":          bairro_obj['lng'],
            "renda_sm":           renda,
            "tipo_moradia":       tipo_casa,
            "tem_menor_18":       tem_menor,
            "escolaridade_baixa": escolaridade_baixa,
            "raca_preta":         raca_preta,
            "doenca_recente":     doenca_recente,
            "saude_mental":       saude_mental,
            "ja_recebe_auxilio":  recebe_auxilio,
            "vulnerabilidade_territorial": vuln_territorial,
            "inseguranca":        classificar_inseguranca(renda, tem_menor, escolaridade_baixa, pts_casa, vuln_territorial),
        }

        contagem_bairros[nome_b] += 1
        i += 1

    with open('data/familias_slz.json', 'w', encoding='utf-8') as f:
        json.dump(familias, f, ensure_ascii=False, indent=4)

    print(f"Sucesso! {total_alvo} famílias geradas e salvas em /data/familias_slz.json")


if __name__ == "__main__":
    gerar_familias()