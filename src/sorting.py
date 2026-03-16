def tem_prioridade(familia_A, familia_B):
    # Dicionário para transformar texto em número de prioridade
    mapa_risco = {
        "Grave": 3, 
        "Moderada": 2,
        "Leve": 1,
        "Seguro": 0
    } 
    
    # Busca os valores, se não tiver insegurança, assume 0
    risco_A = mapa_risco.get(familia_A.get("inseguranca", ""), 0)
    risco_B = mapa_risco.get(familia_B.get("inseguranca", ""), 0)
    
    # 1º Critério: Maior nível de risco
    if risco_A > risco_B:
        return True
    elif risco_A < risco_B:
        return False
    else:
        # 2º Critério (Desempate): Menor renda (agora usando 'renda_pc_sm')
        return familia_A["renda_pc_sm"] < familia_B["renda_pc_sm"]

def merge_sort_familias(lista):
    if len(lista) <= 1:
        return lista
    
    meio = len(lista) // 2
    esquerda = merge_sort_familias(lista[:meio]) # Lembra do fatiamento?
    direita = merge_sort_familias(lista[meio:])
    
    return merge(esquerda, direita)

def merge(esquerda, direita):
    resultado = []
    i = j = 0
    
    while i < len(esquerda) and j < len(direita):
        # Aqui entra a sua regra de negócio!
        if tem_prioridade(esquerda[i], direita[j]):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
            
    # Adiciona o que sobrou
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado