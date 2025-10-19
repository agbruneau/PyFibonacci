from .multiplication import multiply

def fibonacci(n):
    if n == 0:
        return (0, 1)
    else:
        a, b = fibonacci(n // 2)
        c = multiply(a, (2 * b - a))
        d = multiply(a, a) + multiply(b, b)
        if n % 2 == 0:
            return (c, d)
        else:
            return (d, c + d)
