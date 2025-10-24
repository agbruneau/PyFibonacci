"""
Module de répartition pour les opérations de multiplication de haute précision.
"""

import asyncio
from .context import CalculationContext

def _parallel_multiply(a: int, b: int) -> int:
    """
    Fonction cible pour l'exécution parallèle.
    Cette fonction doit être de haut niveau pour être "picklable".
    """
    return a * b

async def multiply(context: CalculationContext, a: int, b: int) -> int:
    """
    Multiplie deux grands entiers, en utilisant une stratégie parallèle si leur
    taille dépasse un certain seuil.

    Args:
        context: Le contexte de calcul contenant le seuil et l'exécuteur de processus.
        a: Le premier entier.
        b: Le deuxième entier.

    Returns:
        Le résultat de la multiplication.
    """
    # Si le parallélisme n'est pas activé, on utilise la multiplication standard.
    if context.executor is None:
        return a * b

    # On détermine si la taille des nombres justifie le coût du parallélisme.
    # n.bit_length() est une manière efficace d'estimer la magnitude d'un nombre.
    # Le seuil est en nombre de chiffres, on fait une conversion approximative (1 chiffre ~ 3.32 bits).
    # log10(2) ~ 0.30103 => 1/log10(2) ~ 3.3219
    if max(a.bit_length(), b.bit_length()) > (context.threshold * 3.3219):
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
