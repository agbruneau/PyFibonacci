"""
Module pour la calibration des performances de multiplication.
"""

import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
from .core.multiplication import _parallel_multiply

async def _measure_standard_multiply(size_in_bits: int) -> float:
    """Mesure le temps d'une multiplication standard pour une certaine taille."""
    # On génère deux nombres aléatoires de la taille spécifiée.
    a = (1 << size_in_bits) - 1
    b = (1 << size_in_bits) - 1

    start_time = time.perf_counter()
    _ = a * b
    end_time = time.perf_counter()
    return end_time - start_time

async def _measure_parallel_multiply(executor: ProcessPoolExecutor, size_in_bits: int) -> float:
    """Mesure le temps d'une multiplication parallèle."""
    a = (1 << size_in_bits) - 1
    b = (1 << size_in_bits) - 1

    loop = asyncio.get_running_loop()

    start_time = time.perf_counter()
    await loop.run_in_executor(executor, _parallel_multiply, a, b)
    end_time = time.perf_counter()
    return end_time - start_time

async def run_calibration(executor: ProcessPoolExecutor):
    """
    Exécute une série de benchmarks pour trouver le seuil optimal pour la multiplication parallèle.
    """
    print("Démarrage de la calibration... (cela peut prendre quelques minutes)")
    print("----------------------------------------------------------------------")
    print("| Taille (bits) | Temps Standard (ms) | Temps Parallèle (ms) | Ratio S/P |")
    print("----------------------------------------------------------------------")

    # On teste des tailles de nombres de plus en plus grandes (en bits).
    # On commence à 10000 bits car en dessous, le parallélisme n'est jamais rentable.
    sizes_to_test = [10000, 20000, 50000, 100000, 200000, 500000]

    for size in sizes_to_test:
        # On fait plusieurs passes pour lisser les résultats.
        standard_times = [await _measure_standard_multiply(size) for _ in range(3)]
        parallel_times = [await _measure_parallel_multiply(executor, size) for _ in range(3)]

        avg_standard = (sum(standard_times) / len(standard_times)) * 1000  # en ms
        avg_parallel = (sum(parallel_times) / len(parallel_times)) * 1000  # en ms

        ratio = avg_standard / avg_parallel if avg_parallel > 0 else float('inf')

        print(f"| {size:<13} | {avg_standard:<19.4f} | {avg_parallel:<20.4f} | {ratio:<9.2f} |")

        if avg_parallel < avg_standard:
            print("----------------------------------------------------------------------")
            print(f"\n>> Seuil optimal approximatif trouvé autour de {size} bits.")
            print(f">> (Equivalent à environ {int(size / 3.3219)} chiffres décimaux)")
            return

    print("----------------------------------------------------------------------")
    print("\n>> Aucun seuil optimal trouvé dans la plage testée. Le parallélisme")
    print(">> n'est peut-être pas avantageux sur cette machine pour ces tailles.")
