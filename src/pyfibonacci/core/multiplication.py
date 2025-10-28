"""
Module de répartition pour les opérations de multiplication de haute précision.
"""

import asyncio
import math
from .context import CalculationContext

def _parallel_multiply(a: int, b: int) -> int:
    """Effectue une multiplication simple `a * b`.

    Cette fonction est conçue pour être exécutée dans un processus séparé via
    `ProcessPoolExecutor`. Pour cette raison, elle doit être une fonction de
    premier niveau dans le module pour garantir qu'elle puisse être "picklée"
    (sérialisée) par le module `multiprocessing`.

    Args:
        a: Le premier entier.
        b: Le deuxième entier.

    Returns:
        Le produit de `a` et `b`.
    """
    return a * b

async def multiply(context: CalculationContext, a: int, b: int) -> int:
    """Multiplie deux entiers en choisissant une stratégie (standard ou parallèle)
    basée sur leur taille.

    Si la taille en bits de l'un des opérandes dépasse un seuil défini dans le
    `CalculationContext`, la multiplication est déléguée à un `ProcessPoolExecutor`
    pour être exécutée dans un processus séparé. Cela est avantageux pour les
    très grands nombres où le coût de la communication inter-processus est
    compensé par le gain de performance du calcul parallèle.

    Args:
        context: Le contexte de calcul contenant le seuil de décision et
                 l'exécuteur de processus.
        a: Le premier entier à multiplier.
        b: Le deuxième entier à multiplier.

    Returns:
        Le produit de `a` et `b`.
    """
    # Si le parallélisme n'est pas activé, on utilise la multiplication standard.
    if context.executor is None:
        return a * b

    # On détermine si la taille des nombres justifie le coût du parallélisme.
    # n.bit_length() est une manière efficace d'estimer la magnitude d'un nombre.
    # Le seuil est en nombre de chiffres, on fait une conversion (1 chiffre ~ 3.32 bits).
    # La conversion exacte est log2(10).
    if max(a.bit_length(), b.bit_length()) > (context.threshold * math.log2(10)):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            context.executor,
            _parallel_multiply,
            a,
            b
        )
    else:
        # Pour les nombres plus petits, la multiplication native est plus rapide.
        return a * b
