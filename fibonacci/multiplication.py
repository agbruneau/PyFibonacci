
"""
This module provides a unified multiplication interface that selects the
optimal algorithm (standard, Karatsuba, or FFT) based on the size of the
input numbers.
"""

from . import karatsuba
from . import fft

# Thresholds for algorithm selection
# These values are placeholders and should be determined by benchmarking.
KARATSUBA_THRESHOLD = 4096
FFT_THRESHOLD = 20000

def multiply(a, b):
    """
    Multiplies two large integers using the most appropriate algorithm.
    """
    size_a = a.bit_length()
    size_b = b.bit_length()

    if size_a < KARATSUBA_THRESHOLD or size_b < KARATSUBA_THRESHOLD:
        return a * b
    elif size_a < FFT_THRESHOLD or size_b < FFT_THRESHOLD:
        return karatsuba.karatsuba(a, b)
    else:
        return fft.multiply(a, b)
