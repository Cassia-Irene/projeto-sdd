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

"""
# Tamanho da família por território
Fonte: Censo IBGE 2022 (média SLZ: 2,96 pessoas/domicílio) + PNAD Contínua.

# Nível 1 (nobre):          2–3 membros  — casais jovens/idosos, nuclear
# Nível 2 (intermediário):  3–4 membros  — operária, alguma extensão
# Nível 3 (vulnerável):     4–6+ membros — multigeracional, Bolsa Família

# Dentro de cada nível, renda muito baixa puxa para o extremo superior da faixa (mais membros) via deslocamento de índice em _sortear_membros.
"""
MEMBROS_POR_TERRITORIO = {
    1: [2, 2, 3, 3],
    2: [2, 3, 3, 4, 4],
    3: [3, 4, 4, 5, 5, 6, 7],
}

def _sortear_membros(vuln_territorial: int, renda: float) -> int:
    """
    Sorteia o número de membros da família considerando território e renda.
 
    Território define a distribuição base (IBGE 2022 por perfil de bairro).
    Renda baixa aumenta a probabilidade de famílias maiores — cada 0,5 SM
    abaixo de 1,5 SM desloca o sorteio um passo para cima na lista.
 
    Exemplo: nível 3, renda 0,3 SM → favorece 5–7 membros.
             nível 1, renda 4,0 SM → favorece 2–3 membros.
    """
    opcoes = MEMBROS_POR_TERRITORIO.get(vuln_territorial, MEMBROS_POR_TERRITORIO[2])
 
    if renda < 1.5:
        desloc = int((1.5 - renda) / 0.5)
        idx = min(desloc, len(opcoes) - 1)
        return random.choice(opcoes[idx:])
 
    return random.choice(opcoes)

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

def _sortear_auxilio(vuln_territorial: int, renda: float, recebe_auxilio_real: bool) -> bool:
    """
    Define se a família já recebe algum auxílio governamental.
 
    Para beneficiários reais da API (recebe_auxilio_real=True), mantém True.
    Para os gerados via Faker, a probabilidade de receber auxílio cresce
    conforme a vulnerabilidade territorial e cai conforme a renda sobe —
    refletindo o critério de elegibilidade do Bolsa Família (renda per capita
    até R$ 218, equivalente a ~0,23 SM em 2024).
 
    Probabilidades base por território:
      Nível 3 (alta vulnerabilidade) → 65% de chance
      Nível 2 (intermediário)        → 35% de chance
      Nível 1 (nobre)                → 5%  de chance
 
    Desconto por renda: cada SM acima de 1.0 reduz a chance em 15pp,
    simulando que famílias com renda mais alta saem do critério de elegibilidade.
    """
    if recebe_auxilio_real:
        return True
 
    base = {3: 0.65, 2: 0.35, 1: 0.05}.get(vuln_territorial, 0.35)
    desconto = max(0.0, (renda - 1.0) * 0.15)
    probabilidade = max(0.0, base - desconto)
 
    return random.random() < probabilidade


def classificar_inseguranca(
        renda: float, 
        membros: int, 
        tem_menor: bool, 
        escolaridade_baixa: bool, 
        pts_moradia: int, 
        vulnerabilidade_territorial: int = 2, 
        ja_recebe_auxilio: bool = False,
) -> str:
    """
    Classifica o nível de insegurança alimentar com base em fatores
    validados pelo diagnóstico MIANMA/SEDES 2024/25 para a Ilha do Maranhão.
 
    Renda per capita é calculada internamente dividindo a renda familiar
    pelo número de membros — uma família de 5 com 1 SM tem renda per capita
    de apenas 0,2 SM, muito pior que um casal com o mesmo salário (0,5 SM).
 
    Sistema de pontuação:
      Renda per capita <= 0.3 SM  → +3 pts  (11,24% IG grave, Tab. 8)
      Renda per capita <= 0.7 SM  → +1 pt   (faixa vulnerável, Tab. 8)
      Tem menor de 18             → +2 pts  (IG grave 10,31% vs 3,56%, Tab. 6)
      Escolaridade baixa          → +1 pt   (IG grave até 14,29%, Tab. 9)
      Moradia precária            → pts variáveis (1–4 conforme tipo)
      Família grande (5+ membros) → +1 pt   (maior pressão alimentar)
      Território nível 3          → +2 pts  (contexto de palafitas/ocupações)
      Território nível 2          → +1 pt   (periferia intermediária)
      Já recebe auxílio           → -1 pt   (rede de proteção parcial)
 
    Resultado:
      score >= 7 → Grave
      score >= 5 → Moderada
      score >= 2 → Leve
      score  < 2 → Seguro
    """
    renda_pc = renda / max(membros, 1)
    score = 0

    if renda_pc <= 0.3:
        score += 3
    elif renda_pc <= 0.7:
        score += 1

    if tem_menor:
        score += 2

    if escolaridade_baixa:
        score += 1

    score += pts_moradia

    if membros >= 5:
        score += 1

    if vulnerabilidade_territorial == 3:
        score += 2
    elif vulnerabilidade_territorial == 2:
        score += 1

    if ja_recebe_auxilio:
        score -= 1

    if score >= 7:   return "Grave"
    elif score >= 5: return "Moderada"
    elif score >= 2: return "Leve"
    return "Seguro"


def buscar_beneficiarios_reais(quantidade: int = 40) -> list:
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


def gerar_familias(total_alvo: int = 80) -> None:
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

        # ── Identidade 
        pessoa_real = i < len(reais)
        if pessoa_real:
            beneficiario     = reais[i]['beneficiarioNovoBolsaFamilia']
            nome_responsavel = beneficiario['nome']
            id_unico         = f"NIS_{beneficiario['nis']}"
        else:
            nome_responsavel = fake.name()
            id_unico         = fake.cpf()

        # ── Variáveis socioeconômicas (calibradas pela SEDES) 
        # Renda e moradia dependem do nível territorial para garantir
        renda              = _sortear_renda_por_territorio(vuln_territorial)
        tipo_casa, pts_casa = tipo_casa, pts_casa = _sortear_moradia_por_territorio(vuln_territorial)

        # Membros: sorteado após renda pois renda baixa puxa para famílias
        # maiores (estrutura multigeracional em áreas vulneráveis).
        membros = _sortear_membros(vuln_territorial, renda)

        prob_menor = PROBABILIDADES["tem_menor_18"]
        if membros >= 4:  # Famílias maiores têm mais chance de ter menores
            prob_menor =
        
        escolaridade_baixa = random.random() < PROBABILIDADES["escolaridade_baixa"]
        raca_preta         = random.random() < PROBABILIDADES["raca_preta"]
        doenca_recente     = random.random() < PROBABILIDADES["doenca_recente"]
        saude_mental       = random.random() < PROBABILIDADES["saude_mental"]
        
        

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