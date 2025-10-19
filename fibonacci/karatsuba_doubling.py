from .karatsuba import karatsuba

def fibonacci(n):
    """
    Calcule F(n) et F(n+1) en utilisant une version optimisée de l'algorithme
    de doublement rapide qui emploie la multiplication de Karatsuba.

    Cette approche combine la complexité logarithmique du doublement rapide
    avec l'efficacité de Karatsuba pour la multiplication de grands nombres.

    Args:
        n (int): L'indice de la suite de Fibonacci à calculer.

    Returns:
        tuple: Un tuple (F(n), F(n+1)).
    """
    if n == 0:
        return (0, 1)
    else:
        a, b = fibonacci(n // 2)
        c = karatsuba(a, (2 * b - a))
        d = karatsuba(a, a) + karatsuba(b, b)
        if n % 2 == 0:
            return (c, d)
        else:
            return (d, c + d)
