"""
Module contenant les implémentations des algorithmes de calcul de Fibonacci.

Ce module fournit plusieurs algorithmes pour calculer le n-ième nombre de
la suite de Fibonacci, chacun avec des caractéristiques de performance
différentes.
"""

import asyncio
from typing import Tuple

from .context import CalculationContext
from .multiplication import multiply


def fib_iterative(n: int) -> int:
    """Calcule F(n) par une approche itérative simple.

    Cette méthode est directe, utilisant une boucle pour construire la suite
    jusqu'à l'indice `n`. Elle est très efficace en mémoire (O(1)), mais sa
    complexité temporelle est linéaire (O(n)), ce qui la rend moins adaptée
    pour de très grandes valeurs de `n` par rapport aux méthodes logarithmiques.

    Args:
        n (int): L'indice (entier non-négatif) dans la suite de Fibonacci.

    Returns:
        int: Le n-ième nombre de Fibonacci.

    Raises:
        ValueError: Si `n` est un entier négatif.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


async def fib_matrix(context: CalculationContext, n: int) -> int:
    """Calcule F(n) via l'exponentiation matricielle.

    Cette méthode repose sur la propriété que F(n) peut être obtenu en élevant
    la matrice [[1, 1], [1, 0]] à la puissance n-1. L'utilisation de
    l'exponentiation par carré confère à cet algorithme une complexité
    temporelle de O(log n).

    Args:
        context (CalculationContext): Le contexte de calcul pour la
            multiplication parallélisée des grands nombres.
        n (int): L'indice (entier non-négatif) de la suite.

    Returns:
        int: Le n-ième nombre de Fibonacci.

    Raises:
        ValueError: Si `n` est un entier négatif.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0

    Matrix = Tuple[int, int, int, int]

    async def multiply_matrices(A: Matrix, B: Matrix) -> Matrix:
        """Multiplie deux matrices 2x2."""
        a, b, c, d = A
        e, f, g, h = B

        ae, bg, af, bh, ce, dg, cf, dh = await asyncio.gather(
            multiply(context, a, e),
            multiply(context, b, g),
            multiply(context, a, f),
            multiply(context, b, h),
            multiply(context, c, e),
            multiply(context, d, g),
            multiply(context, c, f),
            multiply(context, d, h),
        )
        return (ae + bg, af + bh, ce + dg, cf + dh)

    async def matrix_power(A: Matrix, m: int) -> Matrix:
        """Élève une matrice à la puissance m par exponentiation par carré."""
        if m == 0:
            return (1, 0, 0, 1)  # Matrice identité
        if m == 1:
            return A

        if m % 2 == 0:
            half = await matrix_power(A, m // 2)
            return await multiply_matrices(half, half)
        else:
            half = await matrix_power(A, (m - 1) // 2)
            temp = await multiply_matrices(half, half)
            return await multiply_matrices(A, temp)

    F: Matrix = (1, 1, 1, 0)
    result_matrix = await matrix_power(F, n - 1)
    return result_matrix[0]


async def fib_fast_doubling(context: CalculationContext, n: int) -> int:
    """Calcule F(n) via l'algorithme "Fast Doubling".

    Cet algorithme est l'un des plus performants connus, avec une complexité
    temporelle en O(log n). Il utilise des identités mathématiques pour
    calculer F(2k) et F(2k+1) à partir de F(k) et F(k+1).

    Les identités sont :
    F(2k) = F(k) * [2*F(k+1) - F(k)]
    F(2k+1) = F(k+1)^2 + F(k)^2

    Args:
        context (CalculationContext): Le contexte de calcul.
        n (int): L'indice (entier non-négatif) de la suite.

    Returns:
        int: Le n-ième nombre de Fibonacci.

    Raises:
        ValueError: Si `n` est un entier négatif.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0

    async def _fib_fast_doubling(m: int) -> Tuple[int, int]:
        """Fonction récursive qui calcule et retourne (F(m), F(m+1))."""
        if context.progress_queue:
            context.progress_queue.put_nowait(1)

        if m == 0:
            return (0, 1)

        fk, fk1 = await _fib_fast_doubling(m // 2)

        fk_squared, fk1_squared = await asyncio.gather(
            multiply(context, fk, fk), multiply(context, fk1, fk1)
        )

        term = 2 * fk1 - fk
        f2k = await multiply(context, fk, term)
        f2k1 = fk1_squared + fk_squared

        if m % 2 == 0:
            return (f2k, f2k1)
        else:
            return (f2k1, f2k + f2k1)

    result, _ = await _fib_fast_doubling(n)
    return result
