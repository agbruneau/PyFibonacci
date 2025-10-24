"""
Module contenant les implémentations des algorithmes de calcul de la suite de Fibonacci.
"""
import asyncio
from typing import Tuple

from .context import CalculationContext
from .multiplication import multiply


def fib_iterative(n: int) -> int:
    """
    Calcule le n-ième nombre de Fibonacci en utilisant une approche itérative.

    Cette méthode est simple et efficace pour des valeurs de n relativement petites.
    Complexité en temps : O(n)
    Complexité en espace : O(1)

    Args:
        n: L'indice dans la suite de Fibonacci.

    Returns:
        Le n-ième nombre de Fibonacci.
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
    """
    Calcule le n-ième nombre de Fibonacci en utilisant l'exponentiation matricielle.

    Cette méthode est basée sur le fait que :
    [[1, 1], [1, 0]]^n = [[F(n+1), F(n)], [F(n), F(n-1)]]
    Complexité en temps : O(log n)
    Complexité en espace : O(log n) pour la pile d'appels récursifs.

    Args:
        context: Le contexte de calcul.
        n: L'indice dans la suite de Fibonacci.

    Returns:
        Le n-ième nombre de Fibonacci.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0

    async def multiply_matrices(A: Tuple[int, int, int, int], B: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        a, b, c, d = A
        e, f, g, h = B

        ae, bg, af, bh, ce, dg, cf, dh = await asyncio.gather(
            multiply(context, a, e), multiply(context, b, g),
            multiply(context, a, f), multiply(context, b, h),
            multiply(context, c, e), multiply(context, d, g),
            multiply(context, c, f), multiply(context, d, h),
        )
        return (ae + bg, af + bh, ce + dg, cf + dh)

    async def matrix_power(A: Tuple[int, int, int, int], m: int) -> Tuple[int, int, int, int]:
        if m == 0:
            return (1, 0, 0, 1)
        if m == 1:
            return A
        if m % 2 == 0:
            half = await matrix_power(A, m // 2)
            return await multiply_matrices(half, half)
        else:
            half = await matrix_power(A, (m - 1) // 2)
            temp = await multiply_matrices(half, half)
            return await multiply_matrices(A, temp)

    F = (1, 1, 1, 0)

    result_matrix = await matrix_power(F, n - 1)
    return result_matrix[0]

async def fib_fast_doubling(context: CalculationContext, n: int) -> int:
    """
    Calcule le n-ième nombre de Fibonacci en utilisant l'algorithme de "Fast Doubling".

    Cette méthode est l'une des plus rapides connues. Elle est basée sur les identités :
    F(2k) = F(k) * [2*F(k+1) - F(k)]
    F(2k+1) = F(k+1)^2 + F(k)^2
    Complexité en temps : O(log n)
    Complexité en espace : O(log n) pour la pile d'appels récursifs.

    Args:
        context: Le contexte de calcul.
        n: L'indice dans la suite de Fibonacci.

    Returns:
        Le n-ième nombre de Fibonacci.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0

    async def _fib_fast_doubling(m: int) -> Tuple[int, int]:
        if context.progress_queue:
            # Envoie un message pour signifier qu'une étape de la récursion est terminée.
            context.progress_queue.put_nowait(1)

        if m == 0:
            return (0, 1)

        fk, fk1 = await _fib_fast_doubling(m // 2)

        # F(2k) = F(k) * [2*F(k+1) - F(k)]
        # F(2k+1) = F(k+1)^2 + F(k)^2
        fk_squared, fk1_squared = await asyncio.gather(
            multiply(context, fk, fk),
            multiply(context, fk1, fk1)
        )

        term = 2 * fk1 - fk
        f2k = await multiply(context, fk, term)
        f2k1 = fk1_squared + fk_squared

        if m % 2 == 0:
            return (f2k, f2k1)
        else:
            return (f2k1, f2k + f2k1)

    result = await _fib_fast_doubling(n)
    return result[0]
