# 🥗 Ecossistema de Inteligência Alimentar - São Luís/MA

Software de inteligência de dados projetado para apoiar a gestão de segurança alimentar em áreas de vulnerabilidade na capital maranhense, com foco em comunidades ribeirinhas e zonas de risco.

## 📌 Visão Geral
O sistema centraliza dados socioeconómicos e automatiza a análise de risco, permitindo que a gestão pública se antecipe a crises sazonais, como as enchentes características do primeiro semestre em São Luís.

## 🛠️ Engenharia de Dados e Estruturas
O projeto utiliza estruturas de dados otimizadas para garantir performance e integridade no processamento:

* **Dicionários (Hash Maps):** Utilizados para o cadastro unificado de famílias, onde a chave é o identificador único (CPF/NIS). Esta estrutura permite o acesso aos atributos de vulnerabilidade com complexidade de tempo constante $O(1)$.
* **Conjuntos (Sets):** Aplicados na monitoramento da cobertura territorial. Através de operações de diferença, o sistema identifica instantaneamente bairros oficiais que ainda não receberam assistência municipal.
* **Merge Sort (O(n log n)):** Implementação de um algoritmo de ordenação estável e eficiente para priorizar o atendimento. O critério de rankeamento cruza o nível de insegurança alimentar com a renda per capita.
* **Matrizes e Listas:** Estruturas base para o cruzamento de dados geoespaciais e pluviométricos que alimentam o mapa de calor e os gráficos de tendência.

## 📊 Inteligência Visual (Dashboard Interativo)
O sistema gera um painel estratégico em HTML que permite uma análise visual intuitiva:

1.  **Mapa de Calor (Heatmap):** Visualização geoespacial das zonas de risco alimentar utilizando a biblioteca `Folium`.
2.  **Monitoramento Sazonal:** Gráfico que correlaciona o índice de chuvas com alertas de estoque emergencial para famílias sem infraestrutura.
3.  **Perfil de Vulnerabilidade:** Distribuição estatística dos níveis de insegurança (Seguro, Leve, Moderada e Grave).

## 🚀 Como Executar

1.  **Instala as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Gera o Dashboard:**
    ```bash
    python main.py
    ```
3.  **Visualiza o Resultado:**
    Abre o ficheiro `dashboard_slz.html` gerado na raiz do projeto no teu navegador.

## 📂 Arquitetura do Sistema
```text
/
├── /.vscode             # Configurações do ambiente de desenvolvimento
│   └── settings.json
├── /data                # Base de dados e scripts de ETL/Simulação
│   ├── bairros_coords.json
│   ├── chuvas_slz.json
│   ├── classificar_bairros.py
│   ├── entregas_sazonais.json
│   ├── familias_slz.json
│   ├── familias.py
│   ├── gerar_clima.py
│   ├── gerar_entregas.py
│   └── processar_bairros.py
├── /docs                # Documentação adicional e recursos visuais
│   ├── /assets          # Imagens e prints de demonstração do Dashboard
│   └── INFORME.md       # Relatório técnico e apresentação do projeto
├── /src                 # Camadas de processamento e lógica
│   ├── logic.py         # Core: Regras de negócio e análise territorial
│   ├── main.py          # Script de execução dos módulos internos
│   ├── sorting.py       # Algoritmos de Ordenação (Merge Sort)
│   ├── structures.py    # Camada de Acesso a Dados e Modelagem (I/O)
│   └── visuals.py       # Motor de integração com Folium e Chart.js
├── .gitignore           # Arquivos ignorados pelo controle de versão
├── dashboard_slz.html   # Interface visual interativa gerada (Mapas e Gráficos)
├── main.py              # Orquestração e execução central do sistema
├── README.md            # Documentação técnica do ecossistema
└── requirements.txt     # Dependências (Folium, Faker, Pandas, Requests, etc.)
```

## 👩‍💻 Devs
* **Cássia Irene | [GitHub](https://github.com/Cassia-Irene)**
* **Leonardo Ferreira | [GitHub](https://github.com/leonardoferrza)**
* **Melissa Wolff | [GitHub](https://github.com/melwolff13)** 
---
*Projeto desenvolvido para a disciplina de Estruturas de Dados — UNDB.*
