#!/usr/bin/env python3
"""
Calculateur de Suite de Fibonacci de Haute Performance - Version Python
====================================================================

Point d'entrée principal de l'application. Ce module constitue la racine de composition
("composition root") et gère l'initialisation, la configuration, l'orchestration des
modules internes et la gestion du cycle de vie du processus.

Architecture inspirée des principes SOLID et des patrons de conception modernes.
"""

import argparse
import asyncio
import signal
import sys
import time
from typing import Dict, List, Optional, Tuple
import multiprocessing as mp

from fibonacci import Calculator, FastDoubling, MatrixExponentiation, new_calculator
from cli import display_progress, display_results, display_comparison
from fibonacci.utils import validate_config, CalculationResult


# Codes de sortie standards
EXIT_SUCCESS = 0
EXIT_ERROR_GENERIC = 1
EXIT_ERROR_TIMEOUT = 2
EXIT_ERROR_MISMATCH = 3
EXIT_ERROR_CONFIG = 4
EXIT_ERROR_CANCELED = 130


class AppConfig:
    """Configuration de l'application parsée depuis la ligne de commande."""
    
    def __init__(self):
        self.n: int = 1000000
        self.verbose: bool = False
        self.details: bool = False
        self.timeout: int = 300  # secondes
        self.algo: str = "all"
        self.threshold: int = 1000
        self.calibrate: bool = False
    
    def validate(self, available_algos: List[str]) -> bool:
        """Valide la cohérence sémantique de la configuration."""
        if self.timeout <= 0:
            print("Erreur: Le timeout doit être strictement positif", file=sys.stderr)
            return False
        
        if self.threshold < 0:
            print(f"Erreur: Le seuil de parallélisme ne peut être négatif: {self.threshold}", 
                  file=sys.stderr)
            return False
        
        if self.algo != "all" and self.algo not in available_algos:
            print(f"Erreur: Algorithme non reconnu '{self.algo}'. "
                  f"Valeurs valides: 'all' ou {available_algos}", file=sys.stderr)
            return False
        
        return True


# Registre des implémentations d'algorithmes disponibles
CALCULATOR_REGISTRY: Dict[str, type] = {
    "fast": FastDoubling,
    "matrix": MatrixExponentiation,
}


def get_sorted_calculator_keys() -> List[str]:
    """Retourne les clés du registre triées par ordre alphabétique."""
    return sorted(CALCULATOR_REGISTRY.keys())


def parse_arguments() -> Tuple[Optional[AppConfig], int]:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Calculateur de Suite de Fibonacci de Haute Performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py -n 1000000                    # Calcul simple
  python main.py -n 1000000 -algo all -d       # Comparaison détaillée
  python main.py --calibrate                   # Calibration des performances
  python main.py -n 10000000 --timeout 600     # Avec timeout personnalisé
        """
    )
    
    available_algos = get_sorted_calculator_keys()
    algo_help = f"Algorithme à utiliser: 'all' (défaut) ou l'un de {available_algos}"
    
    parser.add_argument("-n", type=int, default=1000000,
                       help="Indice 'n' du nombre de Fibonacci à calculer")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Afficher la valeur complète du résultat")
    parser.add_argument("-d", "--details", action="store_true",
                       help="Afficher les détails de performance")
    parser.add_argument("--timeout", type=int, default=300,
                       help="Délai d'exécution maximal en secondes")
    parser.add_argument("-algo", "--algorithm", dest="algo", default="all",
                       help=algo_help)
    parser.add_argument("--threshold", type=int, default=1000,
                       help="Seuil pour activer la parallélisation")
    parser.add_argument("--calibrate", action="store_true",
                       help="Exécuter le mode de calibration")
    
    try:
        args = parser.parse_args()
        config = AppConfig()
        config.n = args.n
        config.verbose = args.verbose
        config.details = args.details
        config.timeout = args.timeout
        config.algo = args.algo.lower()
        config.threshold = args.threshold
        config.calibrate = args.calibrate
        
        if not config.validate(available_algos):
            return None, EXIT_ERROR_CONFIG
        
        return config, EXIT_SUCCESS
    
    except SystemExit as e:
        return None, e.code if e.code is not None else EXIT_ERROR_CONFIG


async def run_calibration(config: AppConfig) -> int:
    """Exécute le mode calibration pour trouver le seuil optimal."""
    print("--- Mode Calibration : Recherche du Seuil de Parallélisme Optimal ---")
    
    calibration_n = 100000
    calculator = new_calculator(FastDoubling())
    
    thresholds_to_test = [0, 100, 250, 500, 1000, 2000, 4000, 8000]
    results = []
    best_duration = float('inf')
    best_threshold = 0
    
    print(f"Test sur F({calibration_n}) avec différents seuils...")
    
    for threshold in thresholds_to_test:
        threshold_label = f"{threshold}" if threshold > 0 else "Séquentiel"
        print(f"Test du seuil: {threshold_label:<12}...", end=" ", flush=True)
        
        try:
            start_time = time.time()
            await calculator.calculate(n=calibration_n, threshold=threshold)
            duration = time.time() - start_time
            
            print(f"✅ Succès (Durée: {duration:.3f}s)")
            results.append((threshold, duration, None))
            
            if duration < best_duration:
                best_duration = duration
                best_threshold = threshold
                
        except Exception as e:
            print(f"❌ Échec ({e})")
            results.append((threshold, 0, e))
    
    print("\n--- Synthèse de la Calibration ---")
    print(f"{'Seuil':<12} │ {'Durée':<15}")
    print("─" * 14 + "┼" + "─" * 16)
    
    for threshold, duration, error in results:
        threshold_label = f"{threshold}" if threshold > 0 else "Séquentiel"
        duration_str = f"{duration:.3f}s" if error is None else "N/A"
        highlight = " (Optimal)" if threshold == best_threshold and error is None else ""
        print(f"{threshold_label:<12} │ {duration_str:<15}{highlight}")
    
    print(f"\n✅ Recommandation pour cette machine : --threshold {best_threshold}")
    return EXIT_SUCCESS


def get_calculators_to_run(config: AppConfig) -> List[Calculator]:
    """Sélectionne les calculateurs à exécuter selon la configuration."""
    if config.algo == "all":
        return [new_calculator(impl()) for impl in CALCULATOR_REGISTRY.values()]
    else:
        impl_class = CALCULATOR_REGISTRY[config.algo]
        return [new_calculator(impl_class())]


async def execute_calculations(calculators: List[Calculator], config: AppConfig) -> List[CalculationResult]:
    """Orchestre l'exécution concurrente des calculs."""
    print(f"\n--- Début de l'Exécution ---")
    print(f"Calcul de F({config.n}) avec timeout de {config.timeout}s")
    print(f"Environnement: {mp.cpu_count()} CPU, seuil de parallélisation: {config.threshold}")
    
    if len(calculators) > 1:
        print("Mode d'exécution: Comparaison parallèle de tous les algorithmes")
    else:
        print(f"Mode d'exécution: Calcul simple avec l'algorithme {calculators[0].name()}")
    
    # Exécution concurrente des calculs avec timeout
    tasks = []
    for calc in calculators:
        task = asyncio.create_task(
            asyncio.wait_for(
                calc.calculate(n=config.n, threshold=config.threshold),
                timeout=config.timeout
            )
        )
        tasks.append((calc, task))
    
    results = []
    for calc, task in tasks:
        try:
            start_time = time.time()
            result = await task
            duration = time.time() - start_time
            results.append(CalculationResult(calc.name(), result, duration, None))
        except asyncio.TimeoutError:
            duration = config.timeout
            results.append(CalculationResult(calc.name(), None, duration, "Timeout"))
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            results.append(CalculationResult(calc.name(), None, duration, str(e)))
    
    return results


def analyze_comparison_results(results: List[CalculationResult], config: AppConfig) -> int:
    """Analyse et affiche les résultats de comparaison."""
    # Tri des résultats: succès d'abord, puis par durée
    results.sort(key=lambda r: (r.error is not None, r.duration))
    
    successful_results = [r for r in results if r.error is None]
    
    print(f"\n--- Synthèse de la Comparaison ---")
    
    if not successful_results:
        print("❌ Échec: Aucun algorithme n'a pu terminer le calcul")
        display_results(results)
        return EXIT_ERROR_GENERIC
    
    # Validation croisée des résultats
    first_result = successful_results[0].result
    for result in successful_results[1:]:
        if result.result != first_result:
            print("❌ ÉCHEC CRITIQUE: Incohérence détectée entre les résultats!")
            display_comparison(results)
            return EXIT_ERROR_MISMATCH
    
    print("✅ Succès: Tous les résultats valides sont cohérents")
    
    if len(results) > 1:
        display_comparison(results)
    
    # Affichage du résultat du meilleur algorithme
    best_result = successful_results[0]
    display_results([best_result], config.verbose, config.details)
    
    return EXIT_SUCCESS


def setup_signal_handlers():
    """Configure les gestionnaires de signaux pour un arrêt propre."""
    def signal_handler(signum, frame):
        print(f"\n⚠️  Signal {signum} reçu. Arrêt en cours...")
        sys.exit(EXIT_ERROR_CANCELED)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


async def main_async() -> int:
    """Logique principale asynchrone de l'application."""
    config, exit_code = parse_arguments()
    if config is None:
        return exit_code
    
    setup_signal_handlers()
    
    if config.calibrate:
        return await run_calibration(config)
    
    calculators = get_calculators_to_run(config)
    results = await execute_calculations(calculators, config)
    
    return analyze_comparison_results(results, config)


def main() -> int:
    """Point d'entrée principal de l'application."""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⚠️  Interruption par l'utilisateur")
        return EXIT_ERROR_CANCELED
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}", file=sys.stderr)
        return EXIT_ERROR_GENERIC


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)