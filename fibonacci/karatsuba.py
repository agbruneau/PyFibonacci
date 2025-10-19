def karatsuba(x, y):
    """
    Multiplie deux grands entiers en utilisant l'algorithme de Karatsuba.

    Cet algorithme récursif est plus rapide que la multiplication standard
    pour les grands nombres, avec une complexité de O(n^log2(3)).

    Args:
        x (int): Le premier entier.
        y (int): Le deuxième entier.

    Returns:
        int: Le produit de x et y.
    """
    # Base case for recursion
    if x < 10 or y < 10:
        return x * y

    # Calculates the size of the numbers
    m = max(len(str(x)), len(str(y)))
    m2 = m // 2

    # Split the numbers into two halves
    high1, low1 = divmod(x, 10**m2)
    high2, low2 = divmod(y, 10**m2)

    # Recursive steps
    z0 = karatsuba(low1, low2)
    z1 = karatsuba((low1 + high1), (low2 + high2))
    z2 = karatsuba(high1, high2)

    return (z2 * 10**(2 * m2)) + ((z1 - z2 - z0) * 10**m2) + z0
