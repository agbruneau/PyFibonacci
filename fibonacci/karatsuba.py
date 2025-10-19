def karatsuba(x, y):
    """
    Multiplies two large integers using the Karatsuba algorithm.
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
