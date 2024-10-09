import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from scipy import stats
import json
from mathematical_model import GameParameters, Game
from nash_equilibrium_solver import analyze_equilibria

def load_config(config_file='game_config.json'):
    with open(config_file, 'r') as f:
        return json.load(f)
    
def run_simulation(n_simulations=1000):
    params = GameParameters(greed_factor=0.15, group_factor=0.2, community_factor=0.35, stability_factor=0.25, max_bet=80, base_payoff=20, layer1_bonus=10)
    layer1_payoff_results = []
    layer2_payoff_results = []
    community_score_history = []
    reputation_history = []
    cumulative_profit_history = []

    for _ in range(n_simulations):
        time_constraint = np.random.uniform(10, 100)  # Random time constraint for each game
        game = Game(params, time_constraint)
        layer1_payoffs, layer2_payoffs = game.run_game()
        layer1_payoff_results.append(layer1_payoffs)
        layer2_payoff_results.append(layer2_payoffs)
        community_score_history.append(game.community_score)
        reputation_history.append([player.reputation for player in game.layer1_players + game.layer2_players])
        cumulative_profit_history.append([player.cumulative_profit for player in game.layer1_players + game.layer2_players])
        
    return layer1_payoff_results, layer2_payoff_results, community_score_history, reputation_history, cumulative_profit_history

def run_analysis(params, time_constraint):
    print(f"Parameters: {params.__dict__}, time_constraint={time_constraint}")

    try:
        game = Game(params, time_constraint)
        
        # Example type distributions (2 types per player: low sigma and high sigma)
        type_distributions = [[0.7, 0.3] for _ in range(params.n_players)]
        
        ne, bne, cbne = analyze_equilibria(game, type_distributions)

        layer1_payoffs, layer2_payoffs = game.run_game()
        
        print("Layer 1 player payoffs:", layer1_payoffs)
        print("Layer 2 player payoffs:", layer2_payoffs)
        print(f"Total layer 1 profit: {sum(layer1_payoffs)}")
        print(f"Total layer 2 profit: {sum(layer2_payoffs)}")
        print(f"Profit ratio (layer1:layer2): {sum(layer1_payoffs) / sum(layer2_payoffs):.2f}")
        print(f"Total profit: {sum(layer1_payoffs) + sum(layer2_payoffs)}")
        print(f"Base payoff: {params.base_payoff}")
        print(f"Community score: {game.community_score}")
        print(f"Player reputations: {[player.reputation for player in game.layer1_players + game.layer2_players]}")
        print()

        return ne, bne, cbne, sum(layer1_payoffs), sum(layer2_payoffs), game.community_score

    except Exception as e:
        print(f"Error: {str(e)}")
        print()
        return None, None, None, None, None, None

def run_evolutionary_simulation(params, time_constraint, num_generations=10):
    population_size = 1000
    population = np.random.rand(params.n_players, population_size) * params.max_bet  # Initialize with random strategies between 0 and max_bet

    game = Game(params, time_constraint)
    type_distributions = [[0.7, 0.3] for _ in range(params.n_players)]
    ne, _, _ = analyze_equilibria(game, type_distributions)

    if ne is None:
        print("Failed to solve for Nash Equilibrium. Using random initial guess.")
        ne = np.random.rand(params.n_players) * params.max_bet

    avg_strategy_history = []
    fitness_history = []
    nash_distance_history = []

    for generation in range(num_generations):
        fitnesses = np.zeros(population_size)
        for i in range(population_size):
            game = Game(params, time_constraint)
            layer1_payoffs, layer2_payoffs = game.run_game()  # This will set random bets and calculate payoffs
            community_alignment = 1 - np.mean(abs(population[:, i] - np.mean(population[:, i])) / np.mean(population[:, i]))
            fitnesses[i] = max(0, sum(layer1_payoffs) + sum(layer2_payoffs) + params.community_factor * community_alignment * np.mean(population[:, i]) * 5)

        try:
            selected_indices = np.random.choice(population_size, population_size, p=fitnesses / fitnesses.sum())
            population = population[:, selected_indices]
        except ValueError as e:
            print(f"Error in selection: {e}")
            print("Adjusting population.")
            population = np.random.rand(params.n_players, population_size) * 10 + population
            continue

        population += np.random.normal(0, 1, population.shape)
        population = np.clip(population, 0, params.max_bet)

        for _ in range(100):
            parents = np.random.choice(population_size, 2, replace=False)
            crossover_point = np.random.randint(0, params.n_players)
            population[:crossover_point, parents[0]], population[:crossover_point, parents[1]] = \
                population[:crossover_point, parents[1]], population[:crossover_point, parents[0]]

        avg_strategy = population.mean(axis=1)
        avg_strategy_history.append(avg_strategy)
        fitness_history.append(fitnesses.mean())
        nash_distance_history.append(np.linalg.norm(avg_strategy - ne))

        if generation % 2 == 0:
            print(f"Generation {generation}: Average strategy: {avg_strategy}")
            print(f"Generation {generation}: Average fitness: {fitnesses.mean()}")
            print(f"Nash equilibrium: {ne}")
            print(f"Distance from Nash: {nash_distance_history[-1]}")

    final_avg_strategy = population.mean(axis=1)
    print(f"Final average strategy after {num_generations} generations: {final_avg_strategy}")

    return np.array(avg_strategy_history), np.array(nash_distance_history)

def visualize_results(parameter_sets, results):
    fig, axes = plt.subplots(2, 3, figsize=(30, 20))
    fig.suptitle("Game Analysis Results", fontsize=16)

    sns.set_style("whitegrid")

    # Equilibrium Strategy Distribution
    ax = axes[0, 0]
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["ne"] is not None:
            strategies = res["ne"]
            sns.barplot(x=np.arange(len(strategies)), y=strategies, ax=ax, label=f"Set {i+1}")
    ax.set_xlabel("Player")
    ax.set_ylabel("Equilibrium Strategy")
    ax.set_title("Nash Equilibrium Strategies Across Parameter Sets")
    ax.legend()

    # Bayesian Nash Equilibrium
    ax = axes[0, 1]
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["bne"] is not None:
            strategies = res["bne"].mean(axis=1)
            sns.barplot(x=np.arange(len(strategies)), y=strategies, ax=ax, label=f"Set {i+1}")
    ax.set_xlabel("Player")
    ax.set_ylabel("Average Equilibrium Strategy")
    ax.set_title("Bayesian Nash Equilibrium Strategies Across Parameter Sets")
    ax.legend()

    # Community-Focused Bayesian Nash Equilibrium
    ax = axes[0, 2]
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["cbne"] is not None:
            strategies = res["cbne"].mean(axis=1)
            sns.barplot(x=np.arange(len(strategies)), y=strategies, ax=ax, label=f"Set {i+1}")
    ax.set_xlabel("Player")
    ax.set_ylabel("Average Equilibrium Strategy")
    ax.set_title("Community-Focused BNE Strategies Across Parameter Sets")
    ax.legend()

    # Profit Comparison
    ax = axes[1, 0]
    layer1_profits = [res["layer1_profit"] for res in results if res["layer1_profit"] is not None]
    layer2_profits = [res["layer2_profit"] for res in results if res["layer2_profit"] is not None]
    data = pd.DataFrame({
        'Parameter Set': np.repeat(range(1, len(layer1_profits) + 1), 2),
        'Player Type': ['Layer 1', 'Layer 2'] * len(layer1_profits),
        'Profit': layer1_profits + layer2_profits
    })
    sns.barplot(x='Parameter Set', y='Profit', hue='Player Type', data=data, ax=ax)
    ax.set_title("Profit Comparison")
    ax.set_ylim(bottom=min(min(layer1_profits), min(layer2_profits)) - 10, 
                top=max(max(layer1_profits), max(layer2_profits)) + 10)

    # Evolutionary Strategy Progression
    ax = axes[1, 1]
    for i in range(5):
        sns.lineplot(x=range(len(results[0]["avg_strategy_history"])), y=results[0]["avg_strategy_history"][:, i], ax=ax, label=f"Player {i+1}")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Average Strategy")
    ax.set_title("Evolutionary Strategy Progression (Set 1)")

    # Nash Equilibrium Distance
    ax = axes[1, 2]
    for i, res in enumerate(results):
        sns.lineplot(x=range(len(res["nash_distance_history"])), y=res["nash_distance_history"], ax=ax, label=f"Set {i+1}")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Distance from Nash Equilibrium")
    ax.set_title("Nash Equilibrium Distance Over Generations")

    plt.tight_layout()
    plt.savefig("game_analysis_results.png")
    plt.close()

    # Create interactive Plotly visualization
    fig = make_subplots(rows=2, cols=3, subplot_titles=(
        "Nash Equilibrium Strategies",
        "Bayesian Nash Equilibrium Strategies",
        "Community-Focused BNE Strategies",
        "Profit Comparison",
        "Evolutionary Strategy Progression (Set 1)",
        "Nash Equilibrium Distance Over Generations"
    ))

    # Nash Equilibrium Strategies
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["ne"] is not None:
            strategies = res["ne"]
            fig.add_trace(go.Bar(x=np.arange(len(strategies)), y=strategies, name=f"Set {i+1}"), row=1, col=1)

    # Bayesian Nash Equilibrium Strategies
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["bne"] is not None:
            strategies = res["bne"].mean(axis=1)
            fig.add_trace(go.Bar(x=np.arange(len(strategies)), y=strategies, name=f"Set {i+1}"), row=1, col=2)

    # Community-Focused BNE Strategies
    for i, (params, res) in enumerate(zip(parameter_sets, results)):
        if res["cbne"] is not None:
            strategies = res["cbne"].mean(axis=1)
            fig.add_trace(go.Bar(x=np.arange(len(strategies)), y=strategies, name=f"Set {i+1}"), row=1, col=3)

    # Profit Comparison
    fig.add_trace(go.Bar(x=data[data['Player Type'] == 'Layer 1']['Parameter Set'], 
                         y=data[data['Player Type'] == 'Layer 1']['Profit'], 
                         name='Layer 1'), row=2, col=1)
    fig.add_trace(go.Bar(x=data[data['Player Type'] == 'Layer 2']['Parameter Set'], 
                         y=data[data['Player Type'] == 'Layer 2']['Profit'], 
                         name='Layer 2'), row=2, col=1)

    # Evolutionary Strategy Progression
    for i in range(5):
        fig.add_trace(go.Scatter(x=np.arange(len(results[0]["avg_strategy_history"])), 
                                 y=results[0]["avg_strategy_history"][:, i], 
                                 mode='lines', 
                                 name=f"Player {i+1}"), row=2, col=2)

    # Nash Equilibrium Distance
    for i, res in enumerate(results):
        fig.add_trace(go.Scatter(x=np.arange(len(res["nash_distance_history"])), 
                                 y=res["nash_distance_history"], 
                                 mode='lines', 
                                 name=f"Set {i+1}"), row=2, col=3)

    fig.update_layout(height=1200, width=1800, title_text="Interactive Game Analysis Results")
    fig.write_html("interactive_game_analysis_results.html")

def statistical_analysis(results):
    layer1_profits = [res["layer1_profit"] for res in results if res["layer1_profit"] is not None]
    layer2_profits = [res["layer2_profit"] for res in results if res["layer2_profit"] is not None]

    print("\nStatistical Analysis:")
    print(f"Layer 1 Profits: Mean = {np.mean(layer1_profits):.2f}, Variance = {np.var(layer1_profits):.2f}")
    print(f"Layer 2 Profits: Mean = {np.mean(layer2_profits):.2f}, Variance = {np.var(layer2_profits):.2f}")

    t_stat, p_value = stats.ttest_ind(layer1_profits, layer2_profits)
    print(f"T-test results (Layer 1 vs Layer 2 profits): t-statistic = {t_stat:.4f}, p-value = {p_value:.4f}")

if __name__ == "__main__":
    config = load_config()
    parameter_sets = config['parameter_sets']
    
    # Run the general simulation
    print("Running general simulation:")
    layer1_payoff_results, layer2_payoff_results, community_score_history, reputation_history, cumulative_profit_history = run_simulation()
    avg_layer1_payoffs = np.mean(layer1_payoff_results, axis=0)
    avg_layer2_payoffs = np.mean(layer2_payoff_results, axis=0)
    avg_community_score = np.mean(community_score_history)
    avg_reputations = np.mean(reputation_history, axis=0)
    avg_cumulative_profits = np.mean(cumulative_profit_history, axis=0)

    print(f"Average Layer 1 Payoffs: {avg_layer1_payoffs}")
    print(f"Average Layer 2 Payoffs: {avg_layer2_payoffs}")
    print(f"Average Community Score: {avg_community_score}")
    print(f"Average Player Reputations: {avg_reputations}")
    print(f"Average Cumulative Profits: {avg_cumulative_profits}")
    print("\n" + "=" * 50 + "\n")

    # Analyze specific parameter sets
    results = []
    for params in parameter_sets:
        game_params = GameParameters(**params['game_parameters'])
        time_constraint = params['time_constraint']

        print("Running single game analysis:")
        ne, bne, cbne, layer1_profit, layer2_profit, community_score = run_analysis(game_params, time_constraint)
        print("\nRunning evolutionary simulation:")
        avg_strategy_history, nash_distance_history = run_evolutionary_simulation(game_params, time_constraint)
        results.append({
            "ne": ne,
            "bne": bne,
            "cbne": cbne,
            "layer1_profit": layer1_profit,
            "layer2_profit": layer2_profit,
            "avg_strategy_history": avg_strategy_history,
            "nash_distance_history": nash_distance_history,
            "community_score": community_score,
        })
        print("\n" + "=" * 50 + "\n")

    visualize_results(parameter_sets, results)
    statistical_analysis(results)