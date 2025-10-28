"""
Suite de tests de performance (benchmarks) pour les algorithmes de Fibonacci.
"""

import pytest
import asyncio
from pyfibonacci.core.algorithms import fib_iterative, fib_matrix, fib_fast_doubling
from pyfibonacci.core.context import CalculationContext

# Valeur de N pour les benchmarks. Assez grande pour être significative,
# mais assez petite pour ne pas prendre trop de temps.
BENCHMARK_N = 1000

def test_benchmark_iterative(benchmark):
    """Benchmark pour l'algorithme itératif."""
    benchmark(fib_iterative, BENCHMARK_N)

def test_benchmark_matrix(benchmark):
    """Benchmark pour l'algorithme matriciel."""
    context = CalculationContext(threshold=10000)

    def f():
        return asyncio.run(fib_matrix(context, BENCHMARK_N))

    benchmark(f)

def test_benchmark_fast_doubling(benchmark):
    """Benchmark pour l'algorithme 'fast doubling'."""
    context = CalculationContext(threshold=10000)

    def f():
        return asyncio.run(fib_fast_doubling(context, BENCHMARK_N))

    benchmark(f)
