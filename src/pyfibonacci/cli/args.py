"""
Module pour la configuration et l'analyse des arguments de la ligne de commande.
"""

import argparse

def parse_args() -> argparse.Namespace:
    """Configure l'analyseur d'arguments et traite les options de la ligne
    de commande.

    Cette fonction définit toutes les options disponibles pour l'interface
    en ligne de commande, y compris l'indice `n`, le choix de l'algorithme,
    le timeout, et les options de calibration.

    Returns:
        Un objet `argparse.Namespace` contenant les arguments parsés sous
        forme d'attributs.
    """
    parser = argparse.ArgumentParser(
        description="Calculateur de nombres de Fibonacci haute performance en Python.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-n",
        type=int,
        required=False, # Devient optionnel car --calibrate n'en a pas besoin
        help="L'indice du nombre de Fibonacci à calculer."
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
- 'all': Exécute tous les algorithmes disponibles en parallèle."""
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout en secondes pour une seule exécution (par défaut: 10.0)."
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=10000,
        help="""Seuil (nombre de chiffres) à partir duquel la multiplication
parallélisée est utilisée (par défaut: 10000)."""
    )

    parser.add_argument(
        "-d", "--details",
        action="store_true",
        help="Affiche des détails supplémentaires sur l'exécution."
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0",
        help="Affiche la version du programme et quitte."
    )

    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Lance une session de calibration pour déterminer les seuils optimaux."
    )

    return parser.parse_args()
