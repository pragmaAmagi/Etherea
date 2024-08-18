#Copyright (c) [2024] ACME Media Limited
#All rights reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted,
#provided that the above copyright notice appear in all copies and that both the copyright notice and this permission notice appear in supporting documentation, 
#and that the name of ACMe Media Limited not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

#ACME Media Limited DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, 
#IN NO EVENT SHALL ACME Media Limited BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
#LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import numpy as np
from math import isclose
from mathematical_model import pi_i, var_pi_i, cost_function, sigma_squared

def test_pi_i_basic():
    """Test basic functionality of pi_i"""
    n = 3
    alpha = 0.5
    sigmas = [1, 1.5, 2]
    X = [2, 3, 4]
    
    result = pi_i(X[0], X, 0, n, cost_function, alpha, sigmas)
    print(f"Basic pi_i test result: {result}")
    assert isinstance(result, float), "pi_i should return a float"

def test_pi_i_symmetry():
    """Test if pi_i is symmetric for identical players"""
    n = 3
    alpha = 0.5
    sigmas = [1, 1, 1]
    X = [2, 2, 2]
    
    results = [pi_i(X[i], X, i, n, cost_function, alpha, sigmas) for i in range(n)]
    print(f"Symmetry test results: {results}")
    assert all(isclose(results[0], result) for result in results), "pi_i should be symmetric for identical players"

def test_var_pi_i():
    """Test basic functionality of var_pi_i"""
    n = 3
    X = [2, 3, 4]
    
    result = var_pi_i(X, n, sigma_squared)
    print(f"Basic var_pi_i test result: {result}")
    assert isinstance(result, float), "var_pi_i should return a float"
    assert result >= 0, "Variance should be non-negative"

def test_extreme_cases():
    """Test model behavior in extreme cases"""
    n = 3
    alpha = 0.5
    sigmas = [1, 1.5, 2]
    
    # Test with all zero strategies
    X_zeros = [0, 0, 0]
    result_zeros = pi_i(X_zeros[0], X_zeros, 0, n, cost_function, alpha, sigmas)
    print(f"All zeros test result: {result_zeros}")
    
    # Test with very large strategies
    X_large = [1e6, 1e6, 1e6]
    result_large = pi_i(X_large[0], X_large, 0, n, cost_function, alpha, sigmas)
    print(f"Large values test result: {result_large}")

def test_sensitivity():
    """Test sensitivity of the model to small changes in input"""
    n = 3
    alpha = 0.5
    sigmas = [1, 1.5, 2]
    X = [2, 3, 4]
    
    base_result = pi_i(X[0], X, 0, n, cost_function, alpha, sigmas)
    
    # Slightly modify player 0's strategy
    X_modified = [2.01, 3, 4]
    modified_result = pi_i(X_modified[0], X_modified, 0, n, cost_function, alpha, sigmas)
    
    print(f"Base result: {base_result}")
    print(f"Modified result: {modified_result}")
    print(f"Difference: {modified_result - base_result}")

if __name__ == "__main__":
    print("Running model validation tests...")
    test_pi_i_basic()
    test_pi_i_symmetry()
    test_var_pi_i()
    test_extreme_cases()
    test_sensitivity()
    print("All tests completed.")
