"""
Tests pour le module de multiplication.
"""

import asyncio
import pytest
from concurrent.futures import ProcessPoolExecutor

from pyfibonacci.core.context import CalculationContext
from pyfibonacci.core.multiplication import multiply, _parallel_multiply

@pytest.mark.asyncio
async def test_multiply_standard_when_executor_is_none():
    """
    Vérifie que la multiplication standard est utilisée lorsque l'exécuteur
    n'est pas fourni dans le contexte.
    """
    context = CalculationContext(threshold=100, executor=None)
    a, b = 123, 456
    result = await multiply(context, a, b)
    assert result == a * b

@pytest.mark.asyncio
async def test_multiply_standard_for_small_numbers():
    """
    Vérifie que la multiplication standard est utilisée pour des nombres
    inférieurs au seuil, même avec un exécuteur.
    """
    with ProcessPoolExecutor() as executor:
        # Seuil élevé, les nombres sont en dessous.
        context = CalculationContext(threshold=1000, executor=executor)
        a, b = 10**50, 10**50
        result = await multiply(context, a, b)
        assert result == a * b

@pytest.mark.asyncio
async def test_multiply_parallel_for_large_numbers():
    """
    Vérifie que la multiplication parallèle est utilisée pour des nombres
    supérieurs au seuil.
    """
    with ProcessPoolExecutor() as executor:
        # Seuil bas pour forcer le parallélisme.
        # Le seuil est en chiffres, donc 10 est très petit.
        context = CalculationContext(threshold=10, executor=executor)

        # Nombres suffisamment grands pour dépasser le seuil.
        a = 10**100
        b = 10**100

        result = await multiply(context, a, b)
        assert result == a * b

def test_parallel_multiply_function():
    """
    Teste directement la fonction _parallel_multiply pour s'assurer qu'elle
    effectue correctement la multiplication.
    """
    a, b = 987, 654
    assert _parallel_multiply(a, b) == a * b
