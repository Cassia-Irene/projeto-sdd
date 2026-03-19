## 4. Comparação de Algoritmos de Ordenação

### 4.1. Critério de Ordenação Composto

A função `tem_prioridade()` em `src/sorting.py` implementa um critério de ordenação em dois níveis hierárquicos:

- **1º Critério — Nível de insegurança alimentar:** Grave (3) > Moderada (2) > Leve (1) > Seguro (0). Famílias em situação grave recebem atendimento prioritário independentemente da renda.
- **2º Critério (desempate) — Renda per capita em salários mínimos (`renda_pc_sm`):** menor renda = maior prioridade. Este critério desempata quando duas famílias têm o mesmo nível de insegurança, garantindo que a família mais pobre seja atendida primeiro.

### 4.2. Metodologia do Benchmark

Cada algoritmo foi executado sobre listas de 80, 500, 2.000 e 5.000 famílias geradas aleatoriamente pelo `benchmark.py`. Os tempos foram medidos com `time.perf_counter()` e calculados como média de 3 a 5 repetições por tamanho, eliminando variações de cache. O critério de ordenação é idêntico ao usado em `sorting.py`: maior score de risco primeiro, desempate por menor renda per capita.

### 4.3. Resultados

| Algoritmo      | n = 80    | n = 500   | n = 2.000  | n = 5.000   | O()         |
|----------------|-----------|-----------|------------|-------------|-------------|
| Bubble Sort    | 0,28 ms   | 16,01 ms  | 228,40 ms  | 1514,44 ms  | O(n²)       |
| Selection Sort | 0,17 ms   | 9,10 ms   | 175,48 ms  | 785,96 ms   | O(n²)       |
| Insertion Sort | 0,15 ms   | 11,85 ms  | 153,51 ms  | 771,86 ms   | O(n²)       |
| Merge Sort     | 0,11 ms   | 1,85 ms   | 4,74 ms    | 14,53 ms    | O(n log n)  |
| Quick Sort     | 0,05 ms   | 0,85 ms   | 3,14 ms    | 7,82 ms     | O(n log n)  |

### 4.4. Análise dos Resultados

Os dados confirmam empiricamente a diferença entre complexidade O(n²) e O(n log n). Com n = 80 (tamanho real do sistema), todos os algoritmos são equivalentes na prática — a diferença entre Bubble Sort e Merge Sort é de apenas 0,17 ms. Isso explica por que qualquer algoritmo funcionaria para o escopo atual do projeto.

O comportamento diverge rapidamente com o crescimento dos dados. Em n = 5.000 famílias — escala realista para uma secretaria municipal de São Luís — o Bubble Sort leva 1,51 segundo enquanto o Merge Sort resolve em 14,53 ms: uma diferença de **104 vezes**. O Quick Sort foi o mais rápido em todos os tamanhos testados, com 7,82 ms para n = 5.000.

### 4.5. Por que Merge Sort?

A escolha do Merge Sort em detrimento do Quick Sort — mesmo sendo mais lento nos testes — é fundamentada em três propriedades essenciais para este domínio:

- **Estabilidade:** o Merge Sort é estável, ou seja, famílias com o mesmo nível de insegurança alimentar mantêm a ordem relativa original após a ordenação. Isso é relevante quando duas famílias têm o mesmo score de risco e a mesma renda per capita.
- **Complexidade garantida O(n log n):** ao contrário do Quick Sort, o Merge Sort não possui pior caso O(n²). Em dados já ordenados ou com muitos elementos iguais, o Quick Sort pode degradar. Para um sistema de priorização de emergência, a previsibilidade do tempo de execução é um requisito implícito.
- **Implementação recursiva didática:** a natureza divide-e-conquista do algoritmo é transparente no código, facilitando auditoria e manutenção da lógica de priorização.

### 4.6. Análise de Complexidade das Operações do Sistema

| Operação                          | Complexidade | Estrutura / Algoritmo                        |
|-----------------------------------|--------------|----------------------------------------------|
| Acesso a família por CPF/NIS      | O(1)         | Dicionário — hash map                        |
| Verificar se bairro foi atendido  | O(1)         | Conjunto — hash set                          |
| Identificar bairros desassistidos | O(n)         | Diferença de conjuntos                       |
| Ordenar famílias por prioridade   | O(n log n)   | Merge Sort (`sorting.py`)                    |
| Construir ranking de atendimento  | O(n log n)   | Merge Sort sobre lista de dicionários        |
| Somar cestas por coluna da matriz | O(n × m)     | Iteração sobre lista de listas (n bairros × 6 meses) |