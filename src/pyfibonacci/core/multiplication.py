"""
Module de répartition pour la multiplication de haute précision.

Ce module fournit une fonction `multiply` qui agit comme un répartiteur
(dispatcher), choisissant entre une multiplication standard et une
multiplication parallélisée en fonction de la taille des nombres.
"""

import asyncio
import math
from .context import CalculationContext


def _parallel_multiply(a: int, b: int) -> int:
    """Effectue une multiplication simple `a * b` dans un processus séparé.

    Cette fonction est conçue pour être exécutée par un `ProcessPoolExecutor`.
    Elle doit être une fonction de premier niveau pour être sérialisable
    (picklable) par le module `multiprocessing`.

    Args:
        a (int): Le premier opérande.
        b (int): Le second opérande.

    Returns:
        int: Le produit de `a` et `b`.
    """
    return a * b


async def multiply(context: CalculationContext, a: int, b: int) -> int:
    """Multiplie deux entiers, en déléguant si leur taille dépasse un seuil.

    Cette fonction est le cœur de la stratégie de parallélisation. Si la
    magnitude de l'un des nombres (estimée par leur longueur en bits)
    dépasse le seuil configuré dans le `CalculationContext`, la multiplication
    est exécutée dans un processus séparé pour ne pas bloquer la boucle
    d'événements principale.

    Args:
        context (CalculationContext): Le contexte contenant le seuil et
            l'exécuteur de processus.
        a (int): Le premier entier à multiplier.
        b (int): Le second entier à multiplier.

    Returns:
        int: Le produit de `a` et `b`.
    """
    if context.executor is None:
        return a * b

    # Le seuil est en nombre de chiffres décimaux; on le convertit en bits.
    # 1 chiffre décimal équivaut à environ log2(10) bits.
    threshold_in_bits = context.threshold * math.log2(10)

    if max(a.bit_length(), b.bit_length()) > threshold_in_bits:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(context.executor, _parallel_multiply, a, b)
    else:
        # Pour les nombres sous le seuil, la multiplication native est plus rapide.
        return a * b
