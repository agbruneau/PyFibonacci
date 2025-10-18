import pytest
from fibonacci import fast_doubling, matrix_exponentiation

# Test cases for the Fast Doubling algorithm
def test_fast_doubling():
    assert fast_doubling.fibonacci(0)[0] == 0
    assert fast_doubling.fibonacci(1)[0] == 1
    assert fast_doubling.fibonacci(2)[0] == 1
    assert fast_doubling.fibonacci(10)[0] == 55
    assert fast_doubling.fibonacci(20)[0] == 6765
    assert fast_doubling.fibonacci(50)[0] == 12586269025

# Test cases for the Matrix Exponentiation algorithm
def test_matrix_exponentiation():
    assert matrix_exponentiation.fibonacci(0) == 0
    assert matrix_exponentiation.fibonacci(1) == 1
    assert matrix_exponentiation.fibonacci(2) == 1
    assert matrix_exponentiation.fibonacci(10) == 55
    assert matrix_exponentiation.fibonacci(20) == 6765
    assert matrix_exponentiation.fibonacci(50) == 12586269025
