#Copyright (c) [2024] ACME Media Limited
#All rights reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted,
#provided that the above copyright notice appear in all copies and that both the copyright notice and this permission notice appear in supporting documentation, 
#and that the name of ACMe Media Limited not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

#ACME Media Limited DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, 
#IN NO EVENT SHALL ACME Media Limited BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
#LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import numpy as np
from scipy.optimize import minimize
from mathematical_model import pi_i, cost_function


def objective(X, n, cost_function, alpha, sigmas, time_constraint):
    return -sum(
        pi_i(X[i], X, i, n, cost_function, alpha, sigmas, time_constraint)
        for i in range(n)
    )


def solve_nash_equilibrium(n, cost_function, alpha, sigmas, time_constraint):
    initial_guess = np.ones(n) * 500  # Start with a moderate initial guess

    bounds = [(0, 1000) for _ in range(n)]  # Keep the same bounds

    result = minimize(
        objective,
        initial_guess,
        args=(n, cost_function, alpha, sigmas, time_constraint),
        method="L-BFGS-B",
        bounds=bounds,
        options={"ftol": 1e-8, "maxiter": 1000},
    )

    if result.success:
        return result.x
    else:
        raise ValueError(f"Failed to find Nash equilibrium: {result.message}")


def is_nash_equilibrium(
    X, n, cost_function, alpha, sigmas, time_constraint, epsilon=1e-6
):
    for i in range(n):

        def f(x):
            X_copy = X.copy()
            X_copy[i] = x
            return -pi_i(x, X_copy, i, n, cost_function, alpha, sigmas, time_constraint)

        res = minimize(f, X[i], method="L-BFGS-B", bounds=[(0, 1000)])
        if (
            pi_i(res.x[0], X, i, n, cost_function, alpha, sigmas, time_constraint)
            > pi_i(X[i], X, i, n, cost_function, alpha, sigmas, time_constraint)
            + epsilon
        ):
            return False
    return True
