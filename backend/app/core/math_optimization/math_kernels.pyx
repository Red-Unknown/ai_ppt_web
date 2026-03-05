# math_kernels.pyx
import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport sqrt, exp, pow

# Initialize numpy C API
np.import_array()

# -----------------------------------------------------------------------------
# 1. Matrix Operations
# -----------------------------------------------------------------------------

@cython.boundscheck(False)
@cython.wraparound(False)
def matrix_multiply(np.ndarray[np.float64_t, ndim=2] a,
                    np.ndarray[np.float64_t, ndim=2] b):
    """
    High-performance matrix multiplication using Cython.
    Computes C = A * B.
    Optimization: Cache-friendly loop order (i, k, j) and manual unrolling/blocking is hard to beat BLAS.
    But for demonstration, we use the (i, k, j) order which is better than (i, j, k).
    """
    cdef int n = a.shape[0]
    cdef int m = a.shape[1]
    cdef int p = b.shape[1]
    
    if b.shape[0] != m:
        raise ValueError("Matrix dimensions mismatch for multiplication")
        
    cdef np.ndarray[np.float64_t, ndim=2] result = np.zeros((n, p), dtype=np.float64)
    cdef int i, j, k
    cdef double temp
    
    # Optimized loop order: i, k, j
    for i in range(n):
        for k in range(m):
            temp = a[i, k]
            for j in range(p):
                result[i, j] += temp * b[k, j]
                
    return result

# -----------------------------------------------------------------------------
# 2. Numerical Integration
# -----------------------------------------------------------------------------

@cython.boundscheck(False)
@cython.wraparound(False)
def numerical_integration_trapezoidal(np.ndarray[np.float64_t, ndim=1] y, 
                                      double dx):
    """
    Computes numerical integration using the trapezoidal rule.
    """
    cdef int n = y.shape[0]
    cdef double integral = 0.0
    cdef int i
    
    if n < 2:
        return 0.0
        
    for i in range(n - 1):
        integral += (y[i] + y[i+1])
        
    return integral * dx * 0.5

# -----------------------------------------------------------------------------
# 3. Differential Equation Solver (Simple Euler Method)
# -----------------------------------------------------------------------------

# Note: For general ODE solving, we usually pass a Python callable. 
# Calling Python from Cython loop is slow. 
# Here we implement a specialized solver for a common case: dy/dt = -k * y (Decay)
# or just a simple loop demonstration.

@cython.boundscheck(False)
@cython.wraparound(False)
def euler_method_decay(double y0, double k, double dt, int steps):
    """
    Solves dy/dt = -k * y using Euler method.
    """
    cdef np.ndarray[np.float64_t, ndim=1] y = np.zeros(steps + 1, dtype=np.float64)
    cdef np.ndarray[np.float64_t, ndim=1] t = np.zeros(steps + 1, dtype=np.float64)
    cdef int i
    
    y[0] = y0
    t[0] = 0.0
    
    for i in range(steps):
        t[i+1] = t[i] + dt
        y[i+1] = y[i] + (-k * y[i]) * dt
        
    return t, y

# -----------------------------------------------------------------------------
# 4. Statistical Analysis
# -----------------------------------------------------------------------------

@cython.boundscheck(False)
@cython.wraparound(False)
def fast_statistics(np.ndarray[np.float64_t, ndim=1] data):
    """
    Computes mean and variance in a single pass.
    """
    cdef int n = data.shape[0]
    cdef double sum_val = 0.0
    cdef double sum_sq = 0.0
    cdef double val
    cdef int i
    
    if n == 0:
        return 0.0, 0.0
        
    for i in range(n):
        val = data[i]
        sum_val += val
        sum_sq += val * val
        
    cdef double mean = sum_val / n
    cdef double variance = (sum_sq / n) - (mean * mean)
    
    return mean, variance
