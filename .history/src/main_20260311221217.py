from src.visuals import gerar_dashboard_html

if __name__ == "__main__":
    print("="*60)
    print("🚀 INICIANDO ECOSSISTEMA DE INTELIGÊNCIA ALIMENTAR")
    print("="*60)
    
    # Opcional: Aqui você chamaria as funções de gerar_familias() e gerar_clima() 
    # se quisesse que o sistema sempre baixasse dados novos antes de rodar.
    # Mas como os JSONs já estão na pasta data/, vamos direto para a geração do visual.
    
    gerar_dashboard_html()