"""
Point d'entrée principal pour l'interface en ligne de commande (CLI) de PyFibonacci.
"""

import asyncio
import sys
from pyfibonacci.app import main_async

def main():
    # Désactive la limite de conversion int<->str de Python 3.11+
    # Nécessaire pour afficher les très grands nombres de Fibonacci.
    sys.set_int_max_str_digits(0)
    """
    Lance l'application PyFibonacci en initialisant la boucle d'événements asyncio.
    """
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")

if __name__ == "__main__":
    main()
