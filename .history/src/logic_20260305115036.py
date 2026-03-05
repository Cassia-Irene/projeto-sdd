from structures import carregar_bairros, carregar_familias, bairros_atendidos

def identificar_bairros_desassistidos():
    """
    Requisito: Parte 2 - Operações de Conjuntos.
    Usa a diferença de conjuntos para achar bairros oficiais que não estão na lista de atendidos.
    """
    bairros_oficiais = carregar_bairros() # O Set que você acabou de gerar!
    
    # Diferença Simples (-): Retorna o que tem no IBGE/Kaggle mas não tem no nosso registro
    bairros_esquecidos = bairros_oficiais - bairros_atendidos
    
    return bairros_esquecidos

def buscar_familias_criticas():
    """
    Requisito: Parte 2 - Lógica de Cadastro/Busca.
    Filtra o Dicionário buscando famílias com base nas variáveis da Tabela 3.
    """
    familias = carregar_familias()
    familias_prioritarias = {}
    
    for cpf, dados in familias.items():
        # Regras de negócio baseadas na Tabela 3:
        # 1. Renda muito baixa (Var 9)
        # 2. Ausência de saneamento (Var 6)
        # 3. Não recebe auxílio do Portal da Transparência
        renda_baixa = dados.get("renda_sm", 1.0) <= 0.5
        sem_banheiro = dados.get("sem_banheiro", False)
        sem_auxilio = not dados.get("ja_recebe_auxilio", True)
        
        if renda_baixa and sem_banheiro and sem_auxilio:
            familias_prioritarias[cpf] = dados
            
    return familias_prioritarias

if __name__ == "__main__":
    print("="*50)
    print(" 📊 ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR - SLZ")
    print("="*50)
    
    # 1. Testando a Operação de Conjuntos
    desassistidos = identificar_bairros_desassistidos()
    print(f"\n[MAPEAMENTO GEOGRÁFICO]")
    print(f"Total de Bairros (Kaggle): {len(carregar_bairros())}")
    print(f"Bairros Atendidos: {len(bairros_atendidos)}")
    print(f"Pontos Cegos (Desassistidos): {len(desassistidos)}")
    
    # 2. Testando a Busca no Dicionário
    criticas = buscar_familias_criticas()
    print(f"\n[MAPEAMENTO FAMILIAR]")
    print(f"Famílias em Situação Crítica Extrema: {len(criticas)}")
    
    for cpf, f in criticas.items():
        print(f" ⚠️ {f['responsavel']} ({f['bairro']}) | Renda: {f['renda_sm']} SM | Banheiro: Não")