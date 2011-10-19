"""

This algorithm is taken largely from Introduction to Algorithms, 2 ed.
MIT Press

"""
import numpy as np


DTYPE = np.float64

EPS = DTYPE(1E-8)

NEG_EPS = -EPS


def convert_to_slack(A, b, c):
    """ Convert the given standard form to slack form.

    """
    h, w = A.shape
    return np.arange(w, w + h), np.arange(w), A, b, c


def pivot(basic_vars, nonbasic_vars, A, b, c, leaving_var, entering_var):
    pivot_row = basic_vars.index(leaving_var)
    pivot_col = basic_vars.index(entering_var)
    b[pivot_row] =

def do_simplex_iteration(N, B, A, b, c):
    pivot_col_idx = c.argmax()
    col = A[:, pivot_col_idx]
    if np.all(col < EPS):
        raise ValueError('Unbounded solution.')
    else:
        pivot_row_idx = np.nanargmin(b / col) 

    pivot_row = A[pivot_row_idx]
    for idx, row in enumerate(A):
        if idx != pivot_row_idx:
            multiplier = row[pivot_col_idx]
            row[:] = row - multiplier * pivot_row
    

def initialize_simplex(A, b, c, v):
    """ To find a first basic feasible solution, reformulate as:
    
    maximize:                  -x_0

    subject to:     dot(A, x) - x_0 <= b
                                  x >= 0
    
    """
    orig_A = A
    orig_b = b
    orig_c = c
    height, width = orig_A.shape

    # Test to see if the current form is already a basic solution:
    k = orig_b.argmin()
    if orig_b[k] >= NEG_EPS:
        return convert_to_slack(orig_A, orig_b, orig_c)

    
    c = np.array([-1, 0], dtype=DTYPE)

    A = np.empty((h, w + 1), dtype=DTYPE)
    A[:, :w] = orig_A
    A[:, w] = -1.0

    b = np.empty((len(orig_b),), dtype=DTYPE)
    b[:len(orig_b)] = orig_b
    b[-1] = 1

    basic_vars, nonbasic_vars, A, b, c  = convert_to_slack(A, b, c)
    
    # XXX - WTF?
    pivot_row = len(nonbasic_vars) + k
    pivot_col = 0
                                                                                         # basic(row)  # nonbasic(col) 
    basic_vars, nonbasic_vars, A, b, c, v = pivot(basic_vars, non_basic_vars, A, b, c, v, leaving_var, entering_var)

    while np.any(c > NEG_EPS):
        
        N, B, A, b, c, v = do_simplex_iteration(N, B, A, b, c, v)
         
    if 


def simplex(A, b, c, v):
    """ Solve a linear program using the simplex method.
        
        maximize:       dot(c, x)

        subject to:     dot(A, x) <= b
                               x  >= 0

    Paramters
    ---------
    A : (m, n) array
        The array of inequality coefficients
    
    b : (n,) array
        The vector of inequality constants
    
    c : (j,) array
        The vector of objective function coefficients

    Returns
    -------
    x : (j,) array
        The vector of optimal values.
    
    Notes
    -----
    This function will raise an exception if there is not feasible
    solution or if the solution is unbounded.

    """
    N, B, A, b, = initialize_simplex(A, b, c, v)

    while np.any(c > NEG_EPS):
        pass

