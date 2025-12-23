# Written by Juan Pablo Gutierrez
# Date: 2025-12-22
# This file contains the implementation of the Fibonacci 
import time
from typing import Callable

def time_decorator(func: Callable[[int], int]) -> Callable[[int], int]:
    def wrapper(*args, **kwargs) -> int:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"  {func.__name__}({args[0]}) took {elapsed:.9f} seconds")
        return result
    return wrapper

""" 
This is the recursive implementation of the Fibonacci sequence.
"""

def _fib_recursive_internal(n: int) -> int:
    """Internal recursive function without decorator."""
    if n < 2:
        return n
    return _fib_recursive_internal(n-1) + _fib_recursive_internal(n-2)

@time_decorator
def fib_recursive(n: int) -> int:
    """Wrapped version that times only the top-level call."""
    return _fib_recursive_internal(n)

"""
This is the memoization implementation of the Fibonacci sequence.
"""

fib_cache: list[int] = [0, 1]

def _fib_memoization_internal(n: int) -> int:
    """Internal memoization function without decorator."""
    if n < len(fib_cache):
        return fib_cache[n]
    else:
        fib_cache.append(_fib_memoization_internal(n-1) + _fib_memoization_internal(n-2))
        return fib_cache[n]

@time_decorator
def fib_memoization(n: int) -> int:
    """Wrapped version that times only the top-level call."""
    return _fib_memoization_internal(n)

"""
Testing
"""
number = int(input("Enter the number of Fibonacci numbers to calculate: "))

# print("Fibonacci using memoization:")
# result_memo = fib_memoization(number)
# print(f"Result: {result_memo}")
# print()

# print("Fibonacci using recursion:")
# result_rec = fib_recursive(number)
# print(f"Result: {result_rec}")


def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
time_dp = time.time()
print("Fibonacci using dynamic programming:")
result_dp = fib(number)
print(f"Result: {result_dp}")
print(f"Time taken: {time.time() - time_dp:.9f} seconds")