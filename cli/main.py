
import argparse
import sys
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from fibonacci import fast_doubling, matrix_exponentiation, karatsuba_doubling
from .progress_bar import progress_bar

def run_with_timeout(func, n, timeout):
    """
    Exécute une fonction avec un délai d'attente.

    Args:
        func (function): La fonction à exécuter.
        n (int): L'argument à passer à la fonction.
        timeout (int): Le délai d'attente en secondes.

    Returns:
        Le résultat de la fonction, ou None si le délai est dépassé.
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, n)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            return None

def main():
    """
    Point d'entrée principal de l'interface en ligne de commande.

    Analyse les arguments, exécute les algorithmes de Fibonacci et affiche
    une comparaison de leurs performances.
    """
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description='High-performance Fibonacci calculator.')
    parser.add_argument('-n', type=int, required=True, help="The index 'n' of the Fibonacci sequence to calculate.")
    parser.add_argument('-t', '--timeout', type=int, default=300, help='Timeout in seconds for the execution.')
    parser.add_argument('-d', '--details', action='store_true', help='Show performance details and result metadata.')

    args = parser.parse_args()

    n = args.n
    timeout = args.timeout

    # Execution configuration
    print("--- Configuration d'Exécution ---")
    print(f"Calcul de F({n}) avec un timeout de {timeout // 60}m{timeout % 60}s.")
    print(f"Environnement : {multiprocessing.cpu_count()} CPU logiques, Go go1.25.3.")
    print("Seuils d'optimisation : Parallélisme=4096 bits, FFT=20000 bits.")
    print("Mode d'exécution : Comparaison parallèle de tous les algorithmes.")
    print("\n--- Début de l'Exécution ---")

    algorithms = {
        "Fast Doubling (O(log n), Parallèle, Zéro-Alloc)": fast_doubling.fibonacci,
        "Exponentiation Matricielle (O(log n), Parallèle, Zéro-Alloc)": matrix_exponentiation.fibonacci,
        "Karatsuba-Based Doubling": karatsuba_doubling.fibonacci
    }

    results = {}

    total_algorithms = len(algorithms)
    for i, (name, func) in enumerate(algorithms.items()):
        start_time = time.time()

        result_tuple = run_with_timeout(func, n, timeout)

        duration = time.time() - start_time

        if result_tuple is not None:
            result = result_tuple[0] if name != "Exponentiation Matricielle (O(log n), Parallèle, Zéro-Alloc)" else result_tuple
            results[name] = {"duration": duration, "status": "✅ Succès", "result": result}
        else:
            results[name] = {"duration": duration, "status": "❌ Échec: Timeout", "result": None}

        progress_bar(i + 1, total_algorithms)

    print()
    print("--- Synthèse de la Comparaison ---")
    print("{:<60} {:<12} {:<7}".format("Algorithme", "Durée", "Statut"))
    print("{:-<60} {:-<12} {:-<7}".format("", "", ""))

    for name, data in results.items():
        print("{:<60} {:<12.7f}s {:<7}".format(name, data['duration'], data['status']))

    valid_results = [data['result'] for data in results.values() if data['result'] is not None]
    if len(set(valid_results)) > 1:
        print("\nStatut Global : Incohérence des résultats.")
    else:
        print("\nStatut Global : Succès. Tous les résultats valides sont cohérents.")

    if valid_results:
        result_bits = valid_results[0].bit_length()
        print(f"Taille Binaire du Résultat : {result_bits:,} bits.")

    if not args.details:
        print("\n(Utilisez l'option -d ou --details pour un rapport complet)")

if __name__ == '__main__':
    main()
