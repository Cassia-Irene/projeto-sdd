import json
import random
import os

def gerar_historico_sazonal_entregas():
    print("📦 Gerando Matriz de Distribuição Sazonal (Jan-Jun)...")
    
    # 1. Carrega dados base
    with open('data/bairros_coords.json', 'r', encoding='utf-8') as f:
        bairros = json.load(f)
    
    with open('data/chuvas_slz.json', 'r', encoding='utf-8') as f:
        chuvas = json.load(f)

    # 2. Criação da MATRIZ (Lista de Listas: Bairros x Meses)
    # Linha = Bairro | Coluna = Mês (0=Jan, 5=Jun)
    matriz_entregas = []
    historico_tuplas = []

    for b in bairros:
        linha_bairro = []
        for mes_idx in range(6):
            # Lógica: Se o bairro é "atendido" e choveu muito no mês, aumenta a entrega
            chuva_mes = chuvas[mes_idx]['precipitacao']
            base = 15 if b.get('atendido') else 5
            
            # Fator sazonal: quanto mais chuva, mais cestas (simulando emergência)
            fator_chuva = int(chuva_mes / 10) 
            quantidade = base + fator_chuva + random.randint(0, 10)
            
            linha_bairro.append(quantidade)
            
            # 3. Registro em TUPLAS (Imutabilidade para o histórico)
            historico_tuplas.append((chuvas[mes_idx]['mes'], b['nome'], quantidade))
        
        matriz_entregas.append(linha_bairro)

    # 4. Salva os resultados para uso no Dashboard
    dados_finais = {
        "matriz": matriz_entregas,
        "tuplas_registro": historico_tuplas,
        "meses": [c['mes'] for c in chuvas[:6]],
        "bairros": [b['nome'] for b in bairros]
    }

    with open('data/entregas_sazonais.json', 'w', encoding='utf-8') as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    print(f"✅ Matriz de {len(bairros)}x6 gerada e salva com sucesso!")

if __name__ == "__main__":
    gerar_historico_sazonal_entregas()