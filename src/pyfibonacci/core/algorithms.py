"""
Module contenant les implémentations des algorithmes de calcul de la suite de Fibonacci.
"""
import asyncio
from typing import Tuple

from .context import CalculationContext
from .multiplication import multiply


def fib_iterative(n: int) -> int:
    """Calcule le n-ième nombre de Fibonacci en utilisant une approche itérative.

    Cette méthode est une implémentation simple et directe qui construit la
    suite de Fibonacci jusqu'à l'indice `n`. Elle est efficace en mémoire
    (O(1)) mais moins performante en temps (O(n)) que les algorithmes
    logarithmiques pour de grandes valeurs de `n`.

    Args:
        n: L'indice (entier non-négatif) dans la suite de Fibonacci.

    Returns:
        Le n-ième nombre de Fibonacci.

    Raises:
        ValueError: Si `n` est négatif.
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
    """Calcule le n-ième nombre de Fibonacci via l'exponentiation matricielle.

    Cette méthode tire parti de la propriété selon laquelle la n-ième puissance
    de la matrice [[1, 1], [1, 0]] contient les nombres de Fibonacci.
    Elle a une complexité temporelle de O(log n) grâce à l'utilisation de
    l'exponentiation par carré.

    Args:
        context: Le contexte de calcul, utilisé pour la multiplication
                 parallélisée des grands nombres.
        n: L'indice (entier non-négatif) dans la suite de Fibonacci.

    Returns:
        Le n-ième nombre de Fibonacci.

    Raises:
        ValueError: Si `n` est négatif.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0

    async def multiply_matrices(A: Tuple[int, int, int, int], B: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Multiplie deux matrices 2x2 représentées par des tuples."""
        a, b, c, d = A
        e, f, g, h = B

        # Exécute toutes les multiplications en parallèle
        ae, bg, af, bh, ce, dg, cf, dh = await asyncio.gather(
            multiply(context, a, e), multiply(context, b, g),
            multiply(context, a, f), multiply(context, b, h),
            multiply(context, c, e), multiply(context, d, g),
            multiply(context, c, f), multiply(context, d, h),
        )
        # Calcule les nouvelles cellules de la matrice résultante
        return (ae + bg, af + bh, ce + dg, cf + dh)

    async def matrix_power(A: Tuple[int, int, int, int], m: int) -> Tuple[int, int, int, int]:
        """Élève une matrice à la puissance m par exponentiation par carré."""
        if m == 0:
            return (1, 0, 0, 1)  # Matrice identité
        if m == 1:
            return A

        # Si m est pair, A^m = (A^(m/2))^2
        if m % 2 == 0:
            half = await matrix_power(A, m // 2)
            return await multiply_matrices(half, half)
        # Si m est impair, A^m = A * (A^((m-1)/2))^2
        else:
            half = await matrix_power(A, (m - 1) // 2)
            temp = await multiply_matrices(half, half)
            return await multiply_matrices(A, temp)

    # La matrice de base pour Fibonacci
    F = (1, 1, 1, 0)

    # On calcule F^(n-1) car F^k donne F(k+1)
    result_matrix = await matrix_power(F, n - 1)
    return result_matrix[0]

async def fib_fast_doubling(context: CalculationContext, n: int) -> int:
    """Calcule le n-ième nombre de Fibonacci via l'algorithme "Fast Doubling".

    Cet algorithme est l'un des plus efficaces, avec une complexité temporelle
    de O(log n). Il repose sur les identités suivantes pour calculer F(2k) et
    F(2k+1) à partir de F(k) and F(k+1) :
    F(2k) = F(k) * [2*F(k+1) - F(k)]
    F(2k+1) = F(k+1)^2 + F(k)^2

    Args:
        context: Le contexte de calcul, utilisé pour la multiplication
                 parallélisée.
        n: L'indice (entier non-négatif) dans la suite de Fibonacci.

    Returns:
        Le n-ième nombre de Fibonacci.

    Raises:
        ValueError: Si `n` est négatif.
    """
    if n < 0:
        raise ValueError("L'indice de Fibonacci ne peut pas être négatif.")
    if n == 0:
        return 0

    async def _fib_fast_doubling(m: int) -> Tuple[int, int]:
        """Fonction récursive principale pour l'algorithme "Fast Doubling".

        Calcule et retourne la paire (F(m), F(m+1)).

        Args:
            m: L'indice pour lequel calculer la paire de Fibonacci.

        Returns:
            Un tuple contenant F(m) et F(m+1).
        """
        if context.progress_queue:
            # Notifie la barre de progression d'une étape de récursion
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
