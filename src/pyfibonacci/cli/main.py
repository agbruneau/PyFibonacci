"""
Point d'entrée principal pour l'interface en ligne de commande (CLI) de PyFibonacci.
"""

import asyncio
import sys
from pyfibonacci.app import main_async

def main():
    """Point d'entrée principal pour l'exécution synchrone du programme.

    Cette fonction configure l'environnement en désactivant la limite de taille
    pour la conversion d'entiers en chaînes de caractères, ce qui est crucial
    pour manipuler les très grands nombres de Fibonacci. Elle initialise ensuite
    la boucle d'événements asyncio pour lancer l'application principale
    asynchrone et gère une interruption par l'utilisateur (Ctrl+C).
    """
    # Désactive la limite de conversion int<->str de Python 3.11+
    # Nécessaire pour afficher les très grands nombres de Fibonacci.
    sys.set_int_max_str_digits(0)
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")

if __name__ == "__main__":
    main()
