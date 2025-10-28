"""
Module pour la calibration des performances de multiplication.

Ce module fournit les fonctionnalités nécessaires pour déterminer le seuil
optimal à partir duquel la multiplication de grands nombres bénéficie d'une
exécution parallèle via un `ProcessPoolExecutor`. Il compare les performances
de la multiplication standard de Python avec une version parallélisée.
"""

import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
from .core.multiplication import _parallel_multiply


async def _measure_standard_multiply(size_in_bits: int) -> float:
    """Mesure la durée d'une multiplication standard.

    Args:
        size_in_bits (int): La taille en bits des deux nombres à multiplier.
            Les nombres sont générés comme étant `(2**size_in_bits) - 1`.

    Returns:
        float: La durée en secondes de l'opération de multiplication.
    """
    a = (1 << size_in_bits) - 1
    b = (1 << size_in_bits) - 1

    start_time = time.perf_counter()
    _ = a * b
    end_time = time.perf_counter()
    return end_time - start_time


async def _measure_parallel_multiply(
    executor: ProcessPoolExecutor, size_in_bits: int
) -> float:
    """Mesure la durée d'une multiplication parallélisée.

    Args:
        executor (ProcessPoolExecutor): L'instance du pool de processus à
            utiliser pour l'exécution.
        size_in_bits (int): La taille en bits des deux nombres à multiplier.

    Returns:
        float: La durée en secondes de l'opération, incluant la
        sérialisation et la communication inter-processus.
    """
    a = (1 << size_in_bits) - 1
    b = (1 << size_in_bits) - 1

    loop = asyncio.get_running_loop()

    start_time = time.perf_counter()
    await loop.run_in_executor(executor, _parallel_multiply, a, b)
    end_time = time.perf_counter()
    return end_time - start_time


async def run_calibration(executor: ProcessPoolExecutor) -> None:
    """Exécute le processus de calibration pour trouver le seuil de multiplication.

    Cette fonction orchestre une série de tests de performance pour différentes
    tailles de nombres. Elle affiche un tableau comparatif et identifie le
    point où la multiplication parallèle devient plus rapide que la
    multiplication standard.

    Args:
        executor (ProcessPoolExecutor): L'instance du pool de processus à
            utiliser pour les benchmarks de multiplication parallèle.
    """
    print("Démarrage de la calibration... (cela peut prendre quelques minutes)")
    print("----------------------------------------------------------------------")
    print("| Taille (bits) | Temps Standard (ms) | Temps Parallèle (ms) | Ratio S/P |")
    print("----------------------------------------------------------------------")

    sizes_to_test = [10000, 20000, 50000, 100000, 200000, 500000]

    for size in sizes_to_test:
        standard_times = [await _measure_standard_multiply(size) for _ in range(3)]
        parallel_times = [
            await _measure_parallel_multiply(executor, size) for _ in range(3)
        ]

        avg_standard = (sum(standard_times) / len(standard_times)) * 1000  # en ms
        avg_parallel = (sum(parallel_times) / len(parallel_times)) * 1000  # en ms

        ratio = avg_standard / avg_parallel if avg_parallel > 0 else float("inf")

        print(
            f"| {size:<13} | {avg_standard:<19.4f} | {avg_parallel:<20.4f} | {ratio:<9.2f} |"
        )

        if avg_parallel < avg_standard:
            print("----------------------------------------------------------------------")
            print(f"\n>> Seuil optimal approximatif trouvé autour de {size} bits.")
            print(f">> (Equivalent à environ {int(size / 3.3219)} chiffres décimaux)")
            return

    print("----------------------------------------------------------------------")
    print("\n>> Aucun seuil optimal trouvé dans la plage testée. Le parallélisme")
    print(">> n'est peut-être pas avantageux sur cette machine pour ces tailles.")
