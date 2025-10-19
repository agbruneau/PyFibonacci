from .karatsuba import karatsuba

def fibonacci(n):
    """
    Calculates Fibonacci numbers using a fast doubling algorithm with Karatsuba multiplication.
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
