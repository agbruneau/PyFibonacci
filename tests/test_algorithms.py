"""
Suite de tests pour les algorithmes de calcul de Fibonacci.
"""
import asyncio
import pytest
from pyfibonacci.core.algorithms import fib_iterative, fib_matrix, fib_fast_doubling
from pyfibonacci.core.context import CalculationContext

# Les premiers termes de la suite de Fibonacci pour les tests.
FIBONACCI_TERMS = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

@pytest.fixture
def context():
    """Fournit un contexte de calcul de base pour les tests."""
    return CalculationContext(threshold=10000) # Seuil élevé pour ne pas utiliser le parallélisme

@pytest.mark.parametrize("n, expected", enumerate(FIBONACCI_TERMS))
def test_fib_iterative(n, expected):
    """Teste l'algorithme itératif sur des valeurs connues."""
    assert fib_iterative(n) == expected

@pytest.mark.parametrize("n, expected", enumerate(FIBONACCI_TERMS))
@pytest.mark.asyncio
async def test_fib_matrix(context, n, expected):
    """Teste l'algorithme matriciel sur des valeurs connues."""
    result = await fib_matrix(context, n)
    assert result == expected


@pytest.mark.asyncio
async def test_fib_matrix_n_1_edge_case(context):
    """
    Teste spécifiquement le cas n=1 pour fib_matrix.

    Avant le correctif, ce cas était géré par un contournement qui masquait un bug
    de récursion infinie. Ce test s'assure que l'algorithme principal gère
    correctement ce cas critique.
    """
    assert await fib_matrix(context, 1) == 1

@pytest.mark.parametrize("n, expected", enumerate(FIBONACCI_TERMS))
@pytest.mark.asyncio
async def test_fib_fast_doubling(context, n, expected):
    """Teste l'algorithme 'fast doubling' sur des valeurs connues."""
    result = await fib_fast_doubling(context, n)
    assert result == expected

def test_fib_iterative_negative_input():
    """Teste la gestion des entrées négatives pour l'algorithme itératif."""
    with pytest.raises(ValueError):
        fib_iterative(-1)

@pytest.mark.asyncio
async def test_fib_matrix_negative_input(context):
    """Teste la gestion des entrées négatives pour l'algorithme matriciel."""
    with pytest.raises(ValueError):
        await fib_matrix(context, -1)

@pytest.mark.asyncio
async def test_fib_fast_doubling_negative_input(context):
    """Teste la gestion des entrées négatives pour l'algorithme 'fast doubling'."""
    with pytest.raises(ValueError):
        await fib_fast_doubling(context, -1)

# --- Tests basés sur les propriétés avec Hypothesis ---

from hypothesis import given, strategies as st, settings

# On se limite à des entiers raisonnables pour que les tests ne durent pas trop longtemps.
# Hypothesis est assez intelligent pour explorer les bords (0, 1, grands nombres).
INTEGERS_STRATEGY = st.integers(min_value=1, max_value=2000)

@given(n=INTEGERS_STRATEGY)
@settings(max_examples=50, deadline=None) # deadline=None pour les calculs potentiellement longs
@pytest.mark.asyncio
async def test_cassini_identity_fast_doubling(n):
    """
    Valide l'Identité de Cassini pour l'algorithme 'fast doubling'.
    F(n-1) * F(n+1) - F(n)^2 = (-1)^n
    """
    context = CalculationContext(threshold=10000)
    fn_minus_1, fn, fn_plus_1 = await asyncio.gather(
        fib_fast_doubling(context, n - 1),
        fib_fast_doubling(context, n),
        fib_fast_doubling(context, n + 1)
    )

    expected = 1 if n % 2 == 0 else -1

    # L'identité est F(n+1)*F(n-1) - F(n)*F(n)
    result = fn_plus_1 * fn_minus_1 - fn * fn

    assert result == expected
