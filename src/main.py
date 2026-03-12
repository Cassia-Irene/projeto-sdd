from structures import carregar_familias, carregar_bairros
from logic import converter_dict_para_lista, filtrar_por_bairro, buscar_familias_criticas, identificar_bairros_desassistidos, bairros_atendidos

from sorting import merge_sort_familias

def executar_sistema():
    # Carrega os dados usando as funções 
    dict_familias = carregar_familias()
    bairros_validos = carregar_bairros()
    
    # Converte os dados e aplica o algoritmo de ordenação (Merge Sort)
    lista_familias = converter_dict_para_lista(dict_familias)
    familias_priorizadas = merge_sort_familias(lista_familias)
    
    while True:
        print("\n" + "="*80)
        print(" 📊 ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR E HABITACIONAL")
        print("="*80)
        print("1. [Inteligência] Ver TOP 5 Prioridades Gerais (Merge Sort)")
        print("2. [Filtro] Ver Prioridades por Bairro Específico")
        print("3. [Análise] Ver Famílias Críticas (Sem WC + Renda <= 0.5)")
        print("4. [Mapeamento] Ver Bairros Desassistidos")
        print("0. Sair do Sistema")
        print("="*80)
        
        opcao = input("Escolha uma opção numérica: ")
        
        if opcao == "0":
            print("\nEncerrando o sistema...")
            break
            
        elif opcao == "1":
            print("\n--- TOP 5 FAMÍLIAS DE MAIOR RISCO ---")
            for i in range(min(5, len(familias_priorizadas))):
                f = familias_priorizadas[i]
                print(f"{i+1}º Lugar: {f['responsavel']} (CPF: {f['cpf']})")
                print(f"    ↳ Risco: {f['inseguranca']} | Renda: {f['renda_sm']:.2f} SM | Bairro: {f['bairro']}")
                
        elif opcao == "2":
            bairro_digitado = input("\nDigite o nome do bairro com acentos (Ex: Alemanha): ")
            resultado = filtrar_por_bairro(familias_priorizadas, bairro_digitado, bairros_validos)
            if resultado:
                print(f"\n--- TOP 5 PRIORIDADES: {bairro_digitado.upper()} ---")
                for i in range(min(5, len(resultado))):
                    f = resultado[i]
                    print(f"{i+1}º Lugar: {f['responsavel']} (CPF: {f['cpf']}) -> Renda: {f['renda_sm']:.2f} SM")
                    
        elif opcao == "3":
            criticas = buscar_familias_criticas()
            print(f"\n⚠️ [MAPEAMENTO FAMILIAR - CASOS CRÍTICOS]")
            print(f"Total de Famílias Cadastradas: {len(dict_familias)}")
            print(f"Famílias em Situação Crítica (Renda <= 0.5 SM e Sem Banheiro): {len(criticas)}")
            print("-" * 80)
            if not criticas:
                print("Nenhuma família em situação crítica encontrada nos critérios atuais.")
            else:
                for cpf, f in criticas.items():
                    print(f" -> {f['responsavel']} | Bairro: {f['bairro']} | Renda: {f['renda_sm']} SM")
            
        elif opcao == "4":
            desassistidos = identificar_bairros_desassistidos()
            print(f"\n🌍 [MAPEAMENTO GEOGRÁFICO]")
            print(f"Total de Bairros Oficiais: {len(bairros_validos)}")
            print(f"Bairros Atendidos: {len(bairros_atendidos)}")
            print(f"Pontos Cegos (Desassistidos): {len(desassistidos)}")
            
        else:
            print("\nOpção inválida. Tenta novamente.")

if __name__ == "__main__":
    executar_sistema()