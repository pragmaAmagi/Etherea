#Copyright (c) [2024] ACME Media Limited
#All rights reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted,
#provided that the above copyright notice appear in all copies and that both the copyright notice and this permission notice appear in supporting documentation, 
#and that the name of ACMe Media Limited not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

#ACME Media Limited DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, 
#IN NO EVENT SHALL ACME Media Limited BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
#LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import numpy as np

class GameParameters:
    def __init__(self, n_players=5, n_base_players=2, alpha=0.1, beta=0.05, observer_multiplier=1.3, greed_factor=0.2, group_factor=0.3, community_factor=1.0, stability_factor=0.3, max_bet=80, base_payoff=20, layer1_bonus=10):
        self.n_players = n_players
        self.n_base_players = n_base_players
        self.alpha = alpha
        self.beta = beta
        self.observer_multiplier = observer_multiplier
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
        self.layer1_players = self._initialize_players(2)
        self.layer2_players = self._initialize_players(3)
        self.roles = ['bank', 'odd_setter', 'validator']
        self.max_bet = params.max_bet
        self.community_score = 50

    def _initialize_players(self, num_players):
        players = []
        for i in range(num_players):
            sigma = np.random.uniform(0.5, 1.5)
            player = Player(i, 'base' if i < self.params.n_base_players else 'observer', sigma)
            player.game = self
            players.append(player)
        return players

    def run_game(self):
        layer1_bets = [player.place_bet(np.random.uniform(1, self.max_bet)) for player in self.layer1_players]
        layer1_outcome = np.random.choice([True, False])  # 50/50 outcome for layer 1

        layer2_bets = []
        layer2_predictions = []
        for player in self.layer2_players:
            player.make_prediction(np.random.choice([True, False]))
            layer2_predictions.append(player.prediction)
            layer2_bets.append(player.place_bet(np.random.uniform(1, self.max_bet)))

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
        total_bet = sum(bets)
        payoffs = []
        for player, bet, prediction in zip(self.layer2_players, bets, predictions):
            if layer1_outcome == prediction:
                payoff = bet * (total_bet / bet - 1)
            else:
                payoff = -bet
            
            if player.role == 'bank':
                accuracy = 1 - abs(total_bet - sum(predictions)) / total_bet
                payoff *= 1.2 * accuracy
            elif player.role == 'odd_setter':
                actual_odds = sum(predictions) / len(predictions)
                accuracy = 1 - abs(bet/total_bet - actual_odds)
                payoff *= 1.1 * accuracy
            elif player.role == 'validator':
                accuracy = 1 if layer1_outcome == prediction else 0
                payoff *= 1.15 * accuracy
            
            payoffs.append(payoff)
        return payoffs

    def _pi_i(self, x_i, X, i):
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
        self.community_score += 3 if avg_bet <= self.max_bet/2 else -2  # More aggressive community score update
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
