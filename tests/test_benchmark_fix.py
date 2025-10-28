
import pytest
import asyncio
from unittest.mock import patch
from pyfibonacci.core.algorithms import fib_matrix, fib_fast_doubling
from pyfibonacci.core.context import CalculationContext

def test_benchmark_matrix_runs_correctly(benchmark):
    """
    Tests that the benchmark for fib_matrix actually runs the coroutine.
    """
    context = CalculationContext(threshold=10000)
    with patch('pyfibonacci.core.algorithms.multiply') as mock_multiply:
        # Mock the async multiply function
        async def async_multiply(*args):
            return 1
        mock_multiply.side_effect = async_multiply

        def f():
            return asyncio.run(fib_matrix(context, 10))

        benchmark(f)
        assert mock_multiply.called

def test_benchmark_fast_doubling_runs_correctly(benchmark):
    """
    Tests that the benchmark for fib_fast_doubling actually runs the coroutine.
    """
    context = CalculationContext(threshold=10000)
    with patch('pyfibonacci.core.algorithms.multiply') as mock_multiply:
        # Mock the async multiply function
        async def async_multiply(*args):
            return 1
        mock_multiply.side_effect = async_multiply

        def f():
            return asyncio.run(fib_fast_doubling(context, 10))

        benchmark(f)
        assert mock_multiply.called
