import numpy as np

class GameParameters:
    def __init__(self, n_players=5, n_base_players=2, alpha=0.1, beta=0.05, observer_multiplier=1.5, greed_factor=0.2, group_factor=0.3, community_factor=1.0, stability_factor=0.3, max_bet=80, base_payoff=20, layer1_bonus=10):
        self.n_players = n_players
        self.n_base_players = n_base_players
        self.alpha = alpha
        self.beta = beta
        self.observer_multiplier = observer_multiplier  # Increased from 1.3 to 1.5
        self.greed_factor = greed_factor
        self.group_factor = group_factor
        self.community_factor = community_factor
        self.stability_factor = stability_factor
        self.max_bet = max_bet
        self.base_payoff = base_payoff
        self.reputation_factor = 0.4  # Increased from 0.2
        self.layer1_bonus = layer1_bonus

class Player:
    def __init__(self, id, role, sigma):
        self.id = id
        self.role = role
        self.sigma = sigma
        self.bet = 0
        self.vote = None
        self.prediction = None
        self.reputation = 0.5
        self.cumulative_profit = 0
        self.is_observer = False

    def place_bet(self, amount):
        self.bet = min(amount, self.game.max_bet)
        return self.bet

    def cast_vote(self, decision):
        self.vote = decision

    def make_prediction(self, prediction):
        self.prediction = prediction

    def update_cumulative_profit(self, profit):
        self.cumulative_profit += profit

    def copy(self):
        new_player = Player(self.id, self.role, self.sigma)
        new_player.reputation = self.reputation
        new_player.cumulative_profit = self.cumulative_profit
        return new_player

class Game:
    def __init__(self, params, time_constraint):
        self.params = params
        self.time_constraint = time_constraint
        self.layer1_players = self._initialize_players(2, 'base')
        self.layer2_players = self._initialize_players(3, 'observer')
        self.layer3_players = self._initialize_players(0, 'bank')
        self.max_bet = params.max_bet
        self.community_score = 50
        self.roles = ['bank', 'odd_setter', 'validator']  # Restore this line

    def _initialize_players(self, num_players, role):
        players = []
        for i in range(num_players):
            sigma = np.random.uniform(0.5, 1.5)
            player = Player(i, role, sigma)
            player.game = self
            players.append(player)
        return players

    def run_game(self):
        layer1_bets = [player.place_bet(np.random.uniform(1, self.max_bet)) for player in self.layer1_players]
        layer1_outcome = np.random.choice([True, False])

        layer2_bets = []
        layer2_predictions = []
        for player in self.layer2_players:
            player.make_prediction(np.random.choice([True, False]))
            layer2_predictions.append(player.prediction)
            layer2_bets.append(player.place_bet(np.random.uniform(1, self.max_bet)))
            player.is_observer = True  # Ensure all layer 2 players are marked as observers

        # Assign roles, but keep all layer 2 players as observers for payout purposes
        np.random.shuffle(self.roles)
        for player, role in zip(self.layer2_players, self.roles):
            player.role = role

        layer1_payoffs = self._calculate_layer1_payoffs(layer1_bets, layer1_outcome)
        layer2_payoffs = self._calculate_layer2_payoffs(layer2_bets, layer1_outcome, layer2_predictions)

        self.update_community_score(layer1_bets + layer2_bets)
        self.update_reputations(layer1_bets + layer2_bets, layer1_payoffs + layer2_payoffs)
        self.update_cumulative_profits(layer1_payoffs + layer2_payoffs)

        return layer1_payoffs, layer2_payoffs

    def _calculate_layer1_payoffs(self, bets, outcome):
        winner_index = 0 if outcome else 1
        payoffs = [-bet for bet in bets]
        payoffs[winner_index] = sum(bets)
        return payoffs

    def _calculate_layer2_payoffs(self, bets, layer1_outcome, predictions):
        payoffs = []
        disagreement = len(set(predictions)) > 1
        avg_bet = np.mean(bets)

        for player, bet, prediction in zip(self.layer2_players, bets, predictions):
            if prediction is None:
                prediction = np.random.choice([True, False])
            
            # Base payoff calculation
            if layer1_outcome == prediction:
                payoff = bet * self.params.observer_multiplier # Reward for correct prediction
            else:
                payoff = -bet  # Penalty for incorrect prediction

            # Apply community alignment penalty
            bet_deviation = abs(bet - avg_bet) / self.max_bet
            community_penalty = bet_deviation * bet * 0.5  # Adjust the 0.5 factor as needed
            payoff -= community_penalty

            # Role-based bonuses (only if there's disagreement)
            if disagreement:
                if player.role == 'bank':
                    payoff += 20
                elif player.role == 'odd_setter':
                    payoff += 15
                elif player.role == 'validator':
                    payoff += 10

            payoff = max(payoff, 0)  # Ensure non-negative payoff
            payoffs.append(payoff)

            print(f"Player {player.id}: is_observer={player.is_observer}, prediction={prediction}, outcome={layer1_outcome}, payoff={payoff}")

        return payoffs

    def _pi_i(self, x_i, X, i):
        """
        Calculate the individual payoff for a player based on their bet and other game parameters.
        """
        mean_x = np.mean(X)
        sum_x_over_sigma_squared = sum(x_j / player.sigma**2 for x_j, player in zip(X, self.layer1_players + self.layer2_players))
        sum_inverse_sigma_squared = sum(1 / player.sigma**2 for player in self.layer1_players + self.layer2_players)

        time_factor = 1 - np.tanh(self.params.alpha * self.time_constraint / 100)
        group_benefit = (1 - np.exp(-self.params.alpha * np.sqrt(sum(X)))) * x_i * (sum_x_over_sigma_squared / sum_inverse_sigma_squared)
        info_component = np.exp(-((x_i - mean_x) ** 2 / (2 * (self.layer1_players + self.layer2_players)[i].sigma**2)))
        risk_aversion = np.exp(-x_i / 100) * (1 - x_i / self.max_bet) ** 3  # More aggressive risk aversion
        cooperation_bonus = np.exp(-0.005 * abs(x_i - mean_x))  # Increased cooperation bonus

        payoff = self.params.base_payoff + time_factor * (group_benefit + info_component) * risk_aversion * cooperation_bonus

        if i < len(self.layer1_players):
            payoff += self.params.layer1_bonus

        if (self.layer1_players + self.layer2_players)[i].role == 'observer':
            payoff *= self.params.observer_multiplier

        payoff -= self._cost_function(x_i)
        
        community_alignment = 1 - abs(x_i - np.mean(X)) / np.mean(X)
        greed_penalty = self.params.greed_factor * np.exp(x_i / self.max_bet - 0.7) * (1 - community_alignment)
        payoff -= greed_penalty
        
        community_benefit = self.params.community_factor * community_alignment * x_i * 5  # Increased community benefit
        payoff += community_benefit

        stability_bonus = self.params.stability_factor * np.exp(-0.3 * ((x_i - np.mean(X)) / 20)**2) * 2  # Increased stability bonus
        payoff += stability_bonus
        
        reputation_bonus = self.params.reputation_factor * (self.layer1_players + self.layer2_players)[i].reputation * 4  # Increased reputation impact
        payoff += reputation_bonus

        dynamic_base_payoff = self.params.base_payoff * (1 + 0.02 * self.community_score)  # Increased community score impact
        payoff += dynamic_base_payoff - self.params.base_payoff

        return float(np.sum(payoff))

    def _cost_function(self, x):
        return 0.004 * x**1.6  # Slightly more aggressive cost function

    def update_community_score(self, X):
        avg_bet = np.mean(X)
        if avg_bet <= self.max_bet / 2:
            self.community_score += 1  # Less aggressive increase
        else:
            self.community_score -= 1  # Less aggressive decrease
        
        # Consider alignment with community average
        alignment = 1 - np.mean([abs(bet - avg_bet) for bet in X]) / self.max_bet
        self.community_score += alignment * 2  # Reward alignment
        
        self.community_score = max(0, min(100, self.community_score))

    def update_reputations(self, bets, payoffs):
        avg_bet = np.mean(bets)
        for player, bet, payoff in zip(self.layer1_players + self.layer2_players, bets, payoffs):
            bet_score = 1 - abs(bet - avg_bet) / self.max_bet
            payoff_score = (payoff + self.max_bet) / (2 * self.max_bet)
            reputation_change = 0.2 * (bet_score + payoff_score - 1)  # More aggressive reputation change
            player.reputation = max(0, min(1, player.reputation + reputation_change))

    def update_cumulative_profits(self, payoffs):
        for player, payoff in zip(self.layer1_players + self.layer2_players, payoffs):
            player.update_cumulative_profit(payoff)