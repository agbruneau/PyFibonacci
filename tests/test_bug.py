"""
Tests for bug fixes.
"""

import asyncio
import pytest
from concurrent.futures import ProcessPoolExecutor

from pyfibonacci.core.context import CalculationContext
from pyfibonacci.core.multiplication import multiply

class SpyExecutor(ProcessPoolExecutor):
    """An executor that spies on whether its submit method was called."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.was_called = False

    def submit(self, fn, *args, **kwargs):
        self.was_called = True
        return super().submit(fn, *args, **kwargs)

@pytest.mark.asyncio
async def test_multiply_threshold_precision_bug_fix():
    """
    Tests that the corrected threshold logic correctly selects the parallel
    multiplication path for numbers at the boundary.
    """
    executor = SpyExecutor()

    # Use a threshold and number that exposed the original bug.
    # The bit length of 'a' is 11784.
    # The calculated threshold is ~11783.097.
    # 11784 is > 11783.097, so parallel multiplication should be used.
    threshold = 3546
    context = CalculationContext(threshold=threshold, executor=executor)
    a = 2**11783
    b = 2

    # Perform the multiplication.
    result = await multiply(context, a, b)

    # Assert that the result is correct and, crucially, that the parallel
    # executor *was* called.
    assert result == a * b
    assert executor.was_called, "Parallel multiplication was not called."

    executor.shutdown()
