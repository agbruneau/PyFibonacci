def fibonacci(n):
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

from .multiplication import multiply

def multiply_matrices(A, B):
    # This function multiplies two 2x2 matrices
    # and returns the result
    C = [[0, 0], [0, 0]]

    C[0][0] = multiply(A[0][0], B[0][0]) + multiply(A[0][1], B[1][0])
    C[0][1] = multiply(A[0][0], B[0][1]) + multiply(A[0][1], B[1][1])
    C[1][0] = multiply(A[1][0], B[0][0]) + multiply(A[1][1], B[1][0])
    C[1][1] = multiply(A[1][0], B[0][1]) + multiply(A[1][1], B[1][1])

    return C
