
"""
This module implements the Number Theoretic Transform (NTT) for fast
multiplication of large integers. The implementation is based on the principles
described in the Nayuki article on NTT.
"""


def ntt(a, n, root, inverse=False):
    """
    Performs the Number Theoretic Transform (NTT) iteratively.
    """
    N = len(a)

    # Bit-reversal permutation
    j = 0
    for i in range(1, N):
        bit = N >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    # Cooley-Tukey FFT
    len_ = 2
    while len_ <= N:
        w_len = pow(root, (n - 1) // len_, n)
        if inverse:
            w_len = pow(w_len, -1, n)
        i = 0
        while i < N:
            w = 1
            for j in range(len_ // 2):
                u = a[i + j]
                v = (a[i + j + len_ // 2] * w) % n
                a[i + j] = (u + v) % n
                a[i + j + len_ // 2] = (u - v) % n
                w = (w * w_len) % n
            i += len_
        len_ <<= 1

    return a

# Pre-computed NTT primes and their primitive roots
NTT_PRIMES = {
    # N (transform length), (p (prime), g (primitive root))
    2**10: (2**16 + 1, 3),
    2**11: (2**18 * 5 + 1, 3),
    2**12: (2**18 * 7 + 1, 3),
    2**13: (2**18 * 11 + 1, 3),
    2**14: (2**20 * 3 + 1, 3),
    2**15: (2**20 * 5 + 1, 3),
    2**16: (2**22 * 3 + 1, 5),
    2**17: (2**24 * 3 + 1, 3),
    2**18: (2**25 * 3 + 1, 3),
    2**19: (2**25 * 5 + 1, 3),
    2**20: (2**26 * 3 + 1, 5),
}

BASE = 2**16

def to_base(n):
    """
    Converts a large integer to a list of digits in the given base.
    """
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % BASE)
        n //= BASE
    return digits

def multiply(a, b):
    """
    Multiplies two large integers using NTT.
    """
    n_a = to_base(a)
    n_b = to_base(b)

    N = 1
    while N < len(n_a) + len(n_b):
        N <<= 1

    n_a.extend([0] * (N - len(n_a)))
    n_b.extend([0] * (N - len(n_b)))

    if N not in NTT_PRIMES:
        raise ValueError(f"No pre-computed prime for transform size {N}")

    p, root = NTT_PRIMES[N]

    a_ntt = ntt(n_a, p, root)
    b_ntt = ntt(n_b, p, root)

    c_ntt = [(x * y) % p for x, y in zip(a_ntt, b_ntt)]

    c = ntt(c_ntt, p, root, inverse=True)

    inv_N = pow(N, -1, p)
    c = [(x * inv_N) % p for x in c]

    # Reconstruct the number from the polynomial
    result = 0
    carry = 0
    for i in range(N):
        val = c[i] + carry
        result += (val % BASE) * (BASE**i)
        carry = val // BASE

    i = N
    while carry > 0:
        result += (carry % BASE) * (BASE**i)
        carry //= BASE
        i += 1

    return result
