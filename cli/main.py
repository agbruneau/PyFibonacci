import argparse
import time
from fibonacci import fast_doubling, matrix_exponentiation

def main():
    parser = argparse.ArgumentParser(description='High-performance Fibonacci calculator.')
    parser.add_argument('-n', type=int, required=True, help="The index 'n' of the Fibonacci sequence to calculate.")
    parser.add_argument('-algo', type=str, choices=['fast', 'matrix'], required=True, help='Algorithm: fast or matrix.')
    parser.add_argument('-d', '--details', action='store_true', help='Show performance details and result metadata.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show the full value of the result (can be extremely long).')

    args = parser.parse_args()

    n = args.n
    algo = args.algo

    start_time = time.time()

    if algo == 'fast':
        result, _ = fast_doubling.fibonacci(n)
    elif algo == 'matrix':
        result = matrix_exponentiation.fibonacci(n)

    end_time = time.time()
    duration = end_time - start_time

    if args.details:
        print(f"Algorithm: {algo}")
        print(f"Fibonacci({n})")
        print(f"Calculation time: {duration:.6f} seconds")
        print(f"Result length: {len(str(result))} digits")

    if args.verbose:
        print(f"Result: {result}")
    else:
        # Show a truncated result if not in verbose mode
        result_str = str(result)
        if len(result_str) > 100:
            print(f"Result (truncated): {result_str[:50]}...{result_str[-50:]}")
        else:
            print(f"Result: {result_str}")

if __name__ == '__main__':
    main()
