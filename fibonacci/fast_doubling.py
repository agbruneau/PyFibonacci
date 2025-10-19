def fibonacci(n):
    """
    Calcule F(n) et F(n+1) en utilisant l'algorithme de doublement rapide.

    Cette méthode repose sur les identités suivantes :
    F(2k) = F(k) * [2*F(k+1) - F(k)]
    F(2k+1) = F(k)^2 + F(k+1)^2

    Args:
        n (int): L'indice de la suite de Fibonacci à calculer.

    Returns:
        tuple: Un tuple (F(n), F(n+1)).
    """
    if n == 0:
        return (0, 1)
    else:
        a, b = fibonacci(n // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        if n % 2 == 0:
            return (c, d)
        else:
            return (d, c + d)
