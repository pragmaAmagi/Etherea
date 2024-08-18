#Copyright (c) [2024] ACME Media Limited
#All rights reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted,
#provided that the above copyright notice appear in all copies and that both the copyright notice and this permission notice appear in supporting documentation, 
#and that the name of ACMe Media Limited not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

#ACME Media Limited DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, 
#IN NO EVENT SHALL ACME Media Limited BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
#LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import numpy as np
import matplotlib.pyplot as plt
from mathematical_model import pi_i, cost_function, total_profit, get_mixed_strategy
from nash_equilibrium_solver import solve_nash_equilibrium, is_nash_equilibrium


def run_analysis(alpha, sigmas, time_constraint):
    n = len(sigmas)
    print(
        f"Parameters: alpha={alpha}, sigmas={sigmas}, time_constraint={time_constraint}"
    )

    try:
        equilibrium = solve_nash_equilibrium(
            n, cost_function, alpha, sigmas, time_constraint
        )
        print(f"Found equilibrium: {equilibrium}")

        is_ne = is_nash_equilibrium(
            equilibrium, n, cost_function, alpha, sigmas, time_constraint
        )
        print(f"Is Nash equilibrium: {is_ne}")

        total_base_profit = 0
        total_observer_profit = 0

        for i in range(n):
            profit = pi_i(
                equilibrium[i],
                equilibrium,
                i,
                n,
                cost_function,
                alpha,
                sigmas,
                time_constraint,
            )
            player_type = "base player" if i < 2 else "observer"
            print(f"Profit for {player_type} {i}: {profit}")

            if i < 2:
                total_base_profit += profit
            else:
                total_observer_profit += profit

            # Display mixed strategy
            pure_strategies, probabilities = get_mixed_strategy(equilibrium[i])
            print(f"Mixed strategy for player {i}:")
            for ps, prob in zip(pure_strategies, probabilities):
                print(f"  Bet {ps:.2f} with probability {prob:.4f}")

        print(f"Total base player profit: {total_base_profit}")
        print(f"Total observer profit: {total_observer_profit}")
        print(
            f"Profit ratio (base:observer): {total_base_profit / total_observer_profit:.2f}"
        )
        print(
            f"Total profit: {total_profit(equilibrium, n, cost_function, alpha, sigmas, time_constraint)}"
        )
        print()

        return equilibrium, total_base_profit, total_observer_profit
    except Exception as e:
        print(f"Error: {str(e)}")
        print()
        return None, None, None


def run_evolutionary_simulation(alpha, sigmas, time_constraint, num_generations=100):
    n = len(sigmas)
    population = (
        np.random.rand(n, 1000) * 500
    )  # Initialize with random strategies between 0 and 500

    nash_eq = solve_nash_equilibrium(n, cost_function, alpha, sigmas, time_constraint)

    avg_strategy_history = []
    fitness_history = []
    nash_distance_history = []

    for generation in range(num_generations):
        fitnesses = np.array(
            [
                max(
                    0,
                    total_profit(
                        individual, n, cost_function, alpha, sigmas, time_constraint
                    ),
                )
                for individual in population.T
            ]
        )

        # Avoid division by zero
        if fitnesses.sum() == 0:
            print(
                f"Generation {generation}: All fitnesses are zero. Adjusting population."
            )
            population = np.random.rand(n, 1000) * 100 + population  # Add random noise
            continue

        # Selection
        try:
            selected_indices = np.random.choice(
                1000, 1000, p=fitnesses / fitnesses.sum()
            )
            population = population[:, selected_indices]
        except ValueError as e:
            print(f"Error in selection: {e}")
            print("Fitnesses:", fitnesses)
            print("Adjusting population.")
            population = np.random.rand(n, 1000) * 100 + population  # Add random noise
            continue

        # Mutation
        population += np.random.normal(0, 10, population.shape)
        population = np.clip(population, 0, 1000)

        # Crossover
        for _ in range(100):  # Perform 100 crossovers per generation
            parents = np.random.choice(1000, 2, replace=False)
            crossover_point = np.random.randint(0, n)
            (
                population[:crossover_point, parents[0]],
                population[:crossover_point, parents[1]],
            ) = (
                population[:crossover_point, parents[1]],
                population[:crossover_point, parents[0]],
            )

        avg_strategy = population.mean(axis=1)
        avg_strategy_history.append(avg_strategy)
        fitness_history.append(fitnesses.mean())
        nash_distance_history.append(np.linalg.norm(avg_strategy - nash_eq))

        if generation % 10 == 0:
            print(f"Generation {generation}: Average strategy: {avg_strategy}")
            print(f"Generation {generation}: Average fitness: {fitnesses.mean()}")
            print(f"Nash equilibrium: {nash_eq}")
            print(f"Distance from Nash: {nash_distance_history[-1]}")

    final_avg_strategy = population.mean(axis=1)
    print(
        f"Final average strategy after {num_generations} generations: {final_avg_strategy}"
    )

    return np.array(avg_strategy_history), np.array(nash_distance_history)


def visualize_results(parameter_sets, results):
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle("Game Analysis Results", fontsize=16)

    # Equilibrium Strategy Distribution
    ax = axes[0, 0]
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["equilibrium"] is not None:
            strategies = res["equilibrium"]
            ax.bar(
                np.arange(len(strategies)) + i * 0.2,
                strategies,
                width=0.2,
                label=f"Set {i+1}",
            )
    ax.set_xlabel("Player")
    ax.set_ylabel("Equilibrium Strategy")
    ax.set_title("Equilibrium Strategies Across Parameter Sets")
    ax.legend()

    # Profit Comparison
    ax = axes[0, 1]
    base_profits = [
        res["base_profit"] for res in results if res["base_profit"] is not None
    ]
    observer_profits = [
        res["observer_profit"] for res in results if res["observer_profit"] is not None
    ]
    x = np.arange(len(base_profits))
    width = 0.35
    ax.bar(x - width / 2, base_profits, width, label="Base Players")
    ax.bar(x + width / 2, observer_profits, width, label="Observers")
    ax.set_xlabel("Parameter Set")
    ax.set_ylabel("Total Profit")
    ax.set_title("Profit Comparison")
    ax.legend()

    # Evolutionary Strategy Progression
    ax = axes[1, 0]
    for i in range(5):
        ax.plot(results[0]["avg_strategy_history"][:, i], label=f"Player {i+1}")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Average Strategy")
    ax.set_title("Evolutionary Strategy Progression (Set 1)")
    ax.legend()

    # Nash Equilibrium Distance
    ax = axes[1, 1]
    for i, res in enumerate(results):
        ax.plot(res["nash_distance_history"], label=f"Set {i+1}")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Distance from Nash Equilibrium")
    ax.set_title("Nash Equilibrium Distance Over Generations")
    ax.legend()

    plt.tight_layout()

    # Save the figure to a file
    plt.savefig("game_analysis_results.png")  # Save as a PNG file

    plt.show()


if __name__ == "__main__":
    parameter_sets = [
        (0.5, [1, 1, 1.5, 1.5, 1.5], 10),
        (1.0, [1, 1, 1.5, 1.5, 1.5], 20),
        (0.5, [1, 1, 1, 1, 1], 15),
        (0.1, [1, 1, 2, 2, 2], 30),
    ]

    results = []
    for alpha, sigmas, time_constraint in parameter_sets:
        print("Running single game analysis:")
        equilibrium, base_profit, observer_profit = run_analysis(
            alpha, np.array(sigmas), time_constraint
        )
        print("\nRunning evolutionary simulation:")
        avg_strategy_history, nash_distance_history = run_evolutionary_simulation(
            alpha, np.array(sigmas), time_constraint
        )
        results.append(
            {
                "equilibrium": equilibrium,
                "base_profit": base_profit,
                "observer_profit": observer_profit,
                "avg_strategy_history": avg_strategy_history,
                "nash_distance_history": nash_distance_history,
            }
        )
        print("\n" + "=" * 50 + "\n")

    visualize_results(parameter_sets, results)
