import time
import random
import json
import os

# Implementações dos algoritmos

def bubble_sort(lista):
    arr = lista[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j]["score"] < arr[j + 1]["score"]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def selection_sort(lista):
    arr = lista[:]
    n = len(arr)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if arr[j]["score"] > arr[max_idx]["score"]:
                max_idx = j
        arr[i], arr[max_idx] = arr[max_idx], arr[i]
    return arr

def insertion_sort(lista):
    arr = lista[:]
    for i in range(1, len(arr)):
        chave = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["score"] < chave["score"]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = chave
    return arr

def merge_sort(lista):
    if len(lista) <= 1:
        return lista[:]
    meio = len(lista) // 2
    esq = merge_sort(lista[:meio])
    dir = merge_sort(lista[meio:])
    return _merge(esq, dir)

def _merge(esq, dir):
    resultado = []
    i = j = 0
    while i < len(esq) and j < len(dir):
        if esq[i]["score"] >= dir[j]["score"]:
            resultado.append(esq[i]); i += 1
        else:
            resultado.append(dir[j]); j += 1
    resultado.extend(esq[i:])
    resultado.extend(dir[j:])
    return resultado

def quick_sort(lista):
    arr = lista[:]
    _quick_sort_in_place(arr, 0, len(arr) - 1)
    return arr

def _quick_sort_in_place(arr, low, high):
    if low < high:
        pi = _partition(arr, low, high)
        _quick_sort_in_place(arr, low, pi - 1)
        _quick_sort_in_place(arr, pi + 1, high)

def _partition(arr, low, high):
    pivot = arr[high]["score"]
    i = low - 1
    for j in range(low, high):
        if arr[j]["score"] >= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Geração de dados sintéticos

MAPA_RISCO = {"Grave": 3, "Moderada": 2, "Leve": 1, "Seguro": 0}
NIVEIS = ["Grave", "Moderada", "Leve", "Seguro"]
PESOS  = [0.05, 0.20, 0.50, 0.25]

def gerar_familias_sinteticas(n: int):
    familias = []
    for _ in range(n):
        nivel = random.choices(NIVEIS, weights=PESOS, k=1)[0]
        renda_pc = round(random.uniform(0.05, 4.0), 3)
        score = MAPA_RISCO[nivel] * 10 - renda_pc  # score composto
        familias.append({
            "inseguranca": nivel,
            "renda_pc_sm": renda_pc,
            "score": score
        })
    return familias

# Benchmark 

def medir(func, dados, repeticoes=5):
    tempos = []
    for _ in range(repeticoes):
        copia = dados[:]
        t0 = time.perf_counter()
        func(copia)
        tempos.append(time.perf_counter() - t0)
    return round(sum(tempos) / len(tempos) * 1000, 4)  # ms

ALGORITMOS = {
    "Bubble Sort":    bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort":     merge_sort,
    "Quick Sort":     quick_sort,
}

TAMANHOS = [80, 500, 2000, 5000]

def executar_benchmark():
    print("=" * 60)
    print("BENCHMARK — Algoritmos de Ordenação")
    print("Critério: score composto (insegurança + renda per capita)")
    print("=" * 60)

    resultados = {}
    for n in TAMANHOS:
        dados = gerar_familias_sinteticas(n)
        resultados[n] = {}
        print(f"\n▶ n = {n} famílias")
        print(f"  {'Algoritmo':<18} {'Tempo médio (ms)':>18}")
        print(f"  {'-'*36}")
        for nome, func in ALGORITMOS.items():
            rep = 3 if n >= 2000 else 5
            ms = medir(func, dados, repeticoes=rep)
            resultados[n][nome] = ms
            print(f"  {nome:<18} {ms:>17.4f} ms")

    # Persiste resultados
    os.makedirs("data", exist_ok=True)
    with open("data/benchmark_resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("\nResultados salvos em data/benchmark_resultados.json")
    return resultados

if __name__ == "__main__":
    executar_benchmark()