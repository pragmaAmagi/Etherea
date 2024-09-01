#Copyright (c) [2024] ACME Media Limited
#All rights reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted,
#provided that the above copyright notice appear in all copies and that both the copyright notice and this permission notice appear in supporting documentation, 
#and that the name of ACMe Media Limited not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

#ACME Media Limited DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, 
#IN NO EVENT SHALL ACME Media Limited BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
#LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import numpy as np
from scipy.optimize import minimize, differential_evolution
from typing import List, Tuple
from mathematical_model import Game, GameParameters

def objective(X: np.ndarray, game: Game) -> float:
    return -sum(game._pi_i(X[i], X, i) for i in range(len(game.layer1_players + game.layer2_players)))

def solve_nash_equilibrium(game: Game) -> np.ndarray:
    initial_guess = np.ones(len(game.layer1_players + game.layer2_players)) * (game.max_bet / 2)
    bounds = [(0, game.max_bet) for _ in range(len(game.layer1_players + game.layer2_players))]

    methods = ['L-BFGS-B', 'SLSQP', 'TNC']
    
    for method in methods:
        try:
            result = minimize(
                objective,
                initial_guess,
                args=(game,),
                method=method,
                bounds=bounds,
                options={"ftol": 1e-6, "maxiter": 1000},
            )
            
            if result.success:
                return result.x
        except Exception as e:
            print(f"Method {method} failed: {str(e)}")
    
    # If all methods fail, try differential evolution
    try:
        result = differential_evolution(objective, bounds, args=(game,), maxiter=1000, tol=1e-6)
        if result.success:
            return result.x
    except Exception as e:
        print(f"Differential evolution failed: {str(e)}")
    
    # If all optimization methods fail, return a default strategy
    print("Warning: Failed to find Nash equilibrium. Returning default strategy.")
    return np.ones(len(game.layer1_players + game.layer2_players)) * (game.max_bet / 2)

def is_nash_equilibrium(game: Game, X: np.ndarray, epsilon: float = 1e-6) -> bool:
    for i in range(len(game.layer1_players + game.layer2_players)):
        def f(x):
            X_copy = X.copy()
            X_copy[i] = x
            return -game._pi_i(x, X_copy, i)

        res = minimize(f, X[i], method="L-BFGS-B", bounds=[(0, game.max_bet)])
        if game._pi_i(res.x[0], X, i) > game._pi_i(X[i], X, i) + epsilon:
            return False
    return True

def solve_bayesian_nash_equilibrium(game: Game, type_distributions: List[List[float]]) -> List[np.ndarray]:
    n_types = len(type_distributions[0])
    
    def bayesian_objective(X: np.ndarray) -> float:
        strategies = X.reshape(len(game.layer1_players + game.layer2_players), n_types)
        expected_payoff = 0.0
        
        for type_combo in np.ndindex(*[n_types] * len(game.layer1_players + game.layer2_players)):
            prob = np.prod([type_distributions[i][t] for i, t in enumerate(type_combo)])
            game_instance = Game(game.params, game.time_constraint)
            game_instance.layer1_players = [player.copy() for player in game.layer1_players]
            game_instance.layer2_players = [player.copy() for player in game.layer2_players]
            for i, t in enumerate(type_combo):
                if i < len(game.layer1_players):
                    game_instance.layer1_players[i].sigma = 1 + 0.5 * t
                else:
                    game_instance.layer2_players[i - len(game.layer1_players)].sigma = 1 + 0.5 * t
            
            payoffs = [game_instance._pi_i(strategies[i, t], strategies[:, type_combo], i) 
                       for i, t in enumerate(type_combo)]
            expected_payoff += prob * np.sum(payoffs)
        
        return -float(expected_payoff)

    initial_guess = np.ones(len(game.layer1_players + game.layer2_players) * n_types) * (game.max_bet / 2)
    bounds = [(0, game.max_bet) for _ in range(len(game.layer1_players + game.layer2_players) * n_types)]

    try:
        result = minimize(
            bayesian_objective,
            initial_guess,
            method="SLSQP",
            bounds=bounds,
            options={"ftol": 1e-8, "maxiter": 1000},
        )
        
        if not result.success:
            result = differential_evolution(bayesian_objective, bounds, maxiter=1000, tol=1e-8)
        
        if result.success:
            return result.x.reshape(len(game.layer1_players + game.layer2_players), n_types)
        else:
            raise ValueError(f"Failed to find Bayesian Nash equilibrium: {result.message}")
    except Exception as e:
        print(f"Error in BNE solver: {str(e)}")
        return np.ones((len(game.layer1_players + game.layer2_players), n_types)) * (game.max_bet / 2)

def is_bayesian_nash_equilibrium(game: Game, strategies: List[np.ndarray], 
                                 type_distributions: List[List[float]], epsilon: float = 1e-6) -> bool:
    n_types = len(type_distributions[0])
    
    for i in range(len(game.layer1_players + game.layer2_players)):
        for t in range(n_types):
            def f(x):
                strategies_copy = [s.copy() for s in strategies]
                strategies_copy[i][t] = x
                expected_payoff = 0
                
                for type_combo in np.ndindex(*[n_types] * len(game.layer1_players + game.layer2_players)):
                    if type_combo[i] != t:
                        continue
                    prob = np.prod([type_distributions[j][tj] for j, tj in enumerate(type_combo)])
                    game_instance = Game(game.params, game.time_constraint)
                    game_instance.layer1_players = [player.copy() for player in game.layer1_players]
                    game_instance.layer2_players = [player.copy() for player in game.layer2_players]
                    for j, tj in enumerate(type_combo):
                        if j < len(game.layer1_players):
                            game_instance.layer1_players[j].sigma = 1 + 0.5 * tj
                        else:
                            game_instance.layer2_players[j - len(game.layer1_players)].sigma = 1 + 0.5 * tj
                    
                    payoff = game_instance._pi_i(x, [s[tj] for j, (s, tj) in enumerate(zip(strategies_copy, type_combo))], i)
                    expected_payoff += prob * payoff
                
                return -expected_payoff

            res = minimize(f, strategies[i][t], method="L-BFGS-B", bounds=[(0, game.max_bet)])
            if f(strategies[i][t]) > f(res.x[0]) + epsilon:
                return False
    return True

def solve_community_focused_bne(game: Game, type_distributions: List[List[float]]) -> List[np.ndarray]:
    n_types = len(type_distributions[0])
    
    def community_focused_objective(X: np.ndarray) -> float:
        strategies = X.reshape(len(game.layer1_players + game.layer2_players), n_types)
        expected_payoff = 0
        community_benefit = 0

        for type_combo in np.ndindex(*[n_types] * len(game.layer1_players + game.layer2_players)):
            prob = np.prod([type_distributions[i][t] for i, t in enumerate(type_combo)])
            game_instance = Game(game.params, game.time_constraint)
            game_instance.layer1_players = [player.copy() for player in game.layer1_players]
            game_instance.layer2_players = [player.copy() for player in game.layer2_players]
            for i, t in enumerate(type_combo):
                if i < len(game.layer1_players):
                    game_instance.layer1_players[i].sigma = 1 + 0.5 * t
                else:
                    game_instance.layer2_players[i - len(game.layer1_players)].sigma = 1 + 0.5 * t

            payoffs = [game_instance._pi_i(strategies[i, t], strategies[:, type_combo], i) 
                       for i, t in enumerate(type_combo)]
            expected_payoff += prob * np.sum(payoffs)
            community_alignment = 1 - np.mean(abs(strategies[:, type_combo] - np.mean(strategies[:, type_combo])) / np.mean(strategies[:, type_combo]))
            community_benefit += prob * game_instance.params.community_factor * community_alignment * np.mean(strategies[:, type_combo]) * 5

        return -(expected_payoff + community_benefit)

    initial_guess = np.ones(len(game.layer1_players + game.layer2_players) * n_types) * (game.max_bet / 2)
    bounds = [(0, game.max_bet) for _ in range(len(game.layer1_players + game.layer2_players) * n_types)]

    result = minimize(
        community_focused_objective,
        initial_guess,
        method="L-BFGS-B",
        bounds=bounds,
        options={"ftol": 1e-8, "maxiter": 1000},
    )

    if result.success:
        return result.x.reshape(len(game.layer1_players + game.layer2_players), n_types)
    

def analyze_equilibria(game: Game, type_distributions: List[List[float]]) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]:
    print("Solving for Nash Equilibrium...")
    ne = solve_nash_equilibrium(game)
    print(f"Nash Equilibrium: {ne}")
    print(f"Is Nash Equilibrium: {is_nash_equilibrium(game, ne)}")
    
    print("\nSolving for Bayesian Nash Equilibrium...")
    try:
        bne = solve_bayesian_nash_equilibrium(game, type_distributions)
        print(f"Bayesian Nash Equilibrium:\n{bne}")
        print(f"Is Bayesian Nash Equilibrium: {is_bayesian_nash_equilibrium(game, bne, type_distributions)}")
    except Exception as e:
        print(f"Failed to solve BNE: {str(e)}")
        bne = None
    
    print("\nSolving for Community-Focused Bayesian Nash Equilibrium...")
    try:
        cbne = solve_community_focused_bne(game, type_distributions)
        print(f"Community-Focused Bayesian Nash Equilibrium:\n{cbne}")
    except Exception as e:
        print(f"Failed to solve CBNE: {str(e)}")
        cbne = None
    
    return ne, bne, cbne

if __name__ == "__main__":
    # Example usage
    params = GameParameters(n_players=5, n_base_players=2, alpha=0.1, beta=0.05, observer_multiplier=1.3, 
                            greed_factor=0.2, group_factor=0.3, community_factor=1.0, stability_factor=0.3, 
                            max_bet=80, base_payoff=20, reputation_factor=0.4, layer1_bonus=10)
    game = Game(params, time_constraint=10)
    
    # Example type distributions (2 types per player: low sigma and high sigma)
    type_distributions = [[0.7, 0.3] for _ in range(params.n_players)]
    
    ne, bne, cbne = analyze_equilibria(game, type_distributions)
