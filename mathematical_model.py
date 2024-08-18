import numpy as np


def mean_strategy(X):
    return np.mean(X)


def pi_i(x_i, X, i, n, cost_function, alpha, sigmas, time_constraint):
    X_base = X[:2]  # First two elements are base players
    sigma_i = sigmas[i]

    mean_x = mean_strategy(X)

    sum_x_over_sigma_squared = sum(x_j / sigma_j**2 for x_j, sigma_j in zip(X, sigmas))
    sum_inverse_sigma_squared = sum(1 / sigma_j**2 for sigma_j in sigmas)

    # Incorporate time constraint
    time_factor = np.exp(-alpha * time_constraint / 100)

    # Group foraging component with diminishing returns
    group_benefit = (
        (1 - np.exp(-alpha * np.sqrt(sum(X))))
        * x_i
        * (sum_x_over_sigma_squared / sum_inverse_sigma_squared)
    )

    # Incomplete information component
    info_component = np.exp(-((x_i - mean_x) ** 2 / (2 * sigma_i**2 * 1000)))

    # Risk aversion component (strongly favoring lower bets)
    risk_aversion = np.exp(-x_i / 200) * (1 - x_i / 1100) ** 2

    # Cooperation bonus (rewards betting similarly to others)
    cooperation_bonus = np.exp(-0.01 * abs(x_i - mean_x))

    # Additional bonus for lower bets
    low_bet_bonus = np.exp(-0.005 * x_i)

    if i < 2:  # Base player
        payoff = (
            time_factor
            * (group_benefit + info_component)
            * 100
            * risk_aversion
            * cooperation_bonus
            * low_bet_bonus
        )
    else:  # Observer
        observer_factor = 1.2  # Increased from 0.95 to 1.2 to boost observer payoffs
        payoff = (
            observer_factor
            * time_factor
            * (x_i * sum(X_base) / 1000 + info_component)
            * 100
            * risk_aversion
            * cooperation_bonus
            * low_bet_bonus
        )

    return payoff - cost_function(x_i)


def cost_function(x):
    return 0.02 * x**1.5  # Adjusted to make costs grow faster for very high bets


def total_profit(X, n, cost_function, alpha, sigmas, time_constraint):
    return sum(
        pi_i(X[i], X, i, n, cost_function, alpha, sigmas, time_constraint)
        for i in range(n)
    )


def get_mixed_strategy(x, num_pure_strategies=10):
    pure_strategies = np.linspace(0, x, num_pure_strategies)
    probabilities = np.diff(
        np.exp(pure_strategies / 200)
    )  # Adjusted to smooth out probabilities
    probabilities = probabilities / np.sum(probabilities)
    return pure_strategies[1:], probabilities
