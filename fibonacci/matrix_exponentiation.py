def fibonacci(n):
    """
    Calcule F(n) en utilisant l'algorithme d'exponentiation matricielle.

    Cette méthode est basée sur le fait que la matrice de transformation
    [[1, 1], [1, 0]] élevée à la puissance n donne une matrice contenant F(n).

    Args:
        n (int): L'indice de la suite de Fibonacci à calculer.

    Returns:
        int: La valeur de F(n).
    """
    if n == 0:
        return 0

    # The transformation matrix
    T = [[1, 1], [1, 0]]

    # The identity matrix
    result = [[1, 0], [0, 1]]

    # Use binary exponentiation (exponentiation by squaring)
    # to raise the transformation matrix to the power of n
    while n > 0:
        if n % 2 == 1:
            result = multiply_matrices(result, T)
        T = multiply_matrices(T, T)
        n //= 2

    return result[0][1]

def multiply_matrices(A, B):
    """
    Multiplie deux matrices 2x2.

    Args:
        A (list): La première matrice.
        B (list): La deuxième matrice.

    Returns:
        list: Le produit des deux matrices.
    """
    C = [[0, 0], [0, 0]]

    C[0][0] = A[0][0] * B[0][0] + A[0][1] * B[1][0]
    C[0][1] = A[0][0] * B[0][1] + A[0][1] * B[1][1]
    C[1][0] = A[1][0] * B[0][0] + A[1][1] * B[1][0]
    C[1][1] = A[1][0] * B[0][1] + A[1][1] * B[1][1]

    return C
