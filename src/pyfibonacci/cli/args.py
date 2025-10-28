"""
Module pour la configuration et l'analyse des arguments de la ligne de commande.

Ce module utilise le module `argparse` de la bibliothèque standard pour
définir et analyser les arguments fournis par l'utilisateur lors de
l'exécution du programme en ligne de commande.
"""

import argparse


def parse_args() -> argparse.Namespace:
    """Configure et exécute l'analyse des arguments de la ligne de commande.

    Cette fonction met en place un `ArgumentParser` pour gérer toutes les
    options de l'application, telles que l'indice de Fibonacci `n`, le choix
    de l'algorithme, les paramètres de performance (timeout, seuil de
    parallélisation) et les modes spéciaux comme la calibration.

    Returns:
        argparse.Namespace: Un objet contenant les arguments analysés. Chaque
        argument est accessible en tant qu'attribut de cet objet (par exemple,
        `args.n`, `args.algo`).
    """
    parser = argparse.ArgumentParser(
        description="Calculateur de nombres de Fibonacci haute performance en Python.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-n",
        type=int,
        required=False,
        help="L'indice du nombre de Fibonacci à calculer.",
    )

    parser.add_argument(
        "--algo",
        type=str,
        default="fast",
        choices=["iterative", "matrix", "fast", "all"],
        help="""Spécifie l'algorithme à utiliser :
- 'iterative': Méthode itérative simple.
- 'matrix': Méthode d'exponentiation matricielle.
- 'fast': Méthode du 'Fast Doubling' (par défaut).
- 'all': Exécute tous les algorithmes disponibles en parallèle.""",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout en secondes pour une seule exécution (par défaut: 10.0).",
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=10000,
        help="""Seuil (nombre de chiffres) à partir duquel la multiplication
parallélisée est utilisée (par défaut: 10000).""",
    )

    parser.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Affiche des détails supplémentaires sur l'exécution, comme une barre de progression.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
        help="Affiche la version du programme et quitte.",
    )

    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Lance une session de calibration pour déterminer les seuils optimaux.",
    )

    return parser.parse_args()
