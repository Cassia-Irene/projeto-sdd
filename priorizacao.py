import json
from src.sorting import merge_sort_familias

def carregar_dados_reais():
    caminho_arquivo = 'data/familias_slz.json'
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados_brutos = json.load(arquivo)
            familias_lista = []
            for cpf, info in dados_brutos.items():
                familia = {"cpf": cpf}
                familia.update(info)
                familias_lista.append(familia)
            return familias_lista
    except FileNotFoundError:
        return []

def carregar_bairros():
    caminho_arquivo = 'data/bairros_slz.json'
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print("Erro: Ficheiro de bairros não encontrado.")
        return []

def filtrar_por_bairro(familias_ordenadas, bairro_alvo, bairros_validos):
    # 1. Validação: O bairro existe em São Luís (segundo o nosso JSON)?
    if bairro_alvo not in bairros_validos:
        print(f"Aviso: O bairro '{bairro_alvo}' não consta na lista oficial.")
        return []
    
    # 2. Filtragem usando List Comprehension (Eficiência O(n))
    return [f for f in familias_ordenadas if f.get('bairro') == bairro_alvo]

# --- EXECUÇÃO PRINCIPAL (MENU INTERATIVO) ---

familias_reais = carregar_dados_reais()
bairros_validos = carregar_bairros()

if familias_reais and bairros_validos:
    # Ordena TODAS as famílias de uma vez (O(n log n))
    familias_priorizadas = merge_sort_familias(familias_reais)
    
    while True:
        print("\n" + "="*40)
        print("SISTEMA DE TRIAGEM HABITACIONAL")
        print("="*40)
        print("1. Ver TOP 5 Geral (Toda a cidade)")
        print("2. Filtrar fila por Bairro específico")
        print("0. Sair do sistema")
        print("="*40)
        
        opcao = input("Digite o número da opção desejada: ")
        
        if opcao == "0":
            print("\nEncerrando o sistema... Até logo!")
            break # Quebra o laço e sai do programa
            
        elif opcao == "1":
            print("\n--- TOP 5 FAMÍLIAS (GERAL) ---")
            for i in range(min(5, len(familias_priorizadas))):
                f = familias_priorizadas[i]
                print(f"{i+1}º Lugar: {f['responsavel']} (CPF: {f['cpf']})")
                print(f"    ↳ Bairro: {f['bairro']} | Risco: {f['inseguranca']} | Renda: {f['renda_sm']:.2f} SM")
                
        elif opcao == "2":
            bairro_digitado = input("\nDigite o nome do bairro com acentos (ex: Bequimão, Alemanha): ")
            
            resultado_bairro = filtrar_por_bairro(familias_priorizadas, bairro_digitado, bairros_validos)
            
            if resultado_bairro:
                print(f"\n--- TOP 5 PRIORIDADES: {bairro_digitado.upper()} ---")
                for i in range(min(5, len(resultado_bairro))):
                    f = resultado_bairro[i]
                    print(f"{i+1}º Lugar: {f['responsavel']} (CPF: {f['cpf']})")
                    print(f"    ↳ Risco: {f['inseguranca']} | Renda: {f['renda_sm']:.2f} SM")
            # Nota: O aviso de "Bairro não encontrado" já está dentro da sua função filtrar_por_bairro
                
        else:
            print("\nOpção inválida. Tente novamente.")