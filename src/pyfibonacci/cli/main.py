"""
Point d'entrée principal pour l'interface en ligne de commande (CLI).

Ce module sert de lanceur pour l'application PyFibonacci. Sa responsabilité
principale est de configurer l'environnement Python pour la gestion de très
grands nombres et d'initier l'exécution de la logique applicative asynchrone.
"""

import asyncio
import sys
from pyfibonacci.app import main_async


def main() -> None:
    """Point d'entrée synchrone qui initialise et lance l'application asynchrone.

    Cette fonction effectue deux actions critiques :
    1.  Elle configure `sys.set_int_max_str_digits(0)` pour désactiver la
        limite de taille sur la conversion des entiers en chaînes, ce qui est
        indispensable pour les grands nombres de Fibonacci.
    2.  Elle utilise `asyncio.run()` pour démarrer l'exécution de la coroutine
        `main_async`, qui contient la logique principale de l'application.

    La fonction gère également l'exception `KeyboardInterrupt` pour permettre
    une sortie propre si l'utilisateur interrompt le programme.
    """
    # Désactive la limite de conversion int<->str, nécessaire pour les grands nombres.
    sys.set_int_max_str_digits(0)
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")


if __name__ == "__main__":
    main()
