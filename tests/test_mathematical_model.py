import unittest
from unittest.mock import Mock
import numpy as np
from ..mathematical_model import GameParameters, Player, Game


class TestGameParameters(unittest.TestCase):
    def test_game_parameters_initialization(self):
        params = GameParameters()
        self.assertEqual(params.n_players, 5)
        self.assertEqual(params.n_base_players, 2)
        self.assertEqual(params.alpha, 0.1)
        self.assertEqual(params.beta, 0.05)
        self.assertEqual(params.observer_multiplier, 1.5)
        self.assertEqual(params.greed_factor, 0.2)
        self.assertEqual(params.group_factor, 0.3)
        self.assertEqual(params.community_factor, 1.0)
        self.assertEqual(params.stability_factor, 0.3)
        self.assertEqual(params.max_bet, 80)
        self.assertEqual(params.base_payoff, 20)
        self.assertEqual(params.layer1_bonus, 10)
        self.assertEqual(params.reputation_factor, 0.4)

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player(id=1, role='base', sigma=1.0)

    def test_player_initialization(self):
        self.assertEqual(self.player.id, 1)
        self.assertEqual(self.player.role, 'base')
        self.assertEqual(self.player.sigma, 1.0)
        self.assertEqual(self.player.bet, 0)
        self.assertIsNone(self.player.vote)
        self.assertIsNone(self.player.prediction)
        self.assertEqual(self.player.reputation, 0.5)
        self.assertEqual(self.player.cumulative_profit, 0)
        self.assertFalse(self.player.is_observer)

    def test_place_bet(self):
        self.player.game = Mock(max_bet=100)
        self.assertEqual(self.player.place_bet(50), 50)
        self.assertEqual(self.player.place_bet(150), 100)

    def test_cast_vote(self):
        self.player.cast_vote(True)
        self.assertTrue(self.player.vote)

    def test_make_prediction(self):
        self.player.make_prediction(False)
        self.assertFalse(self.player.prediction)

    def test_update_cumulative_profit(self):
        self.player.update_cumulative_profit(100)
        self.assertEqual(self.player.cumulative_profit, 100)
        self.player.update_cumulative_profit(-50)
        self.assertEqual(self.player.cumulative_profit, 50)

class TestGame(unittest.TestCase):
    def setUp(self):
        params = GameParameters()
        self.game = Game(params, time_constraint=100)

    def test_game_initialization(self):
        self.assertEqual(len(self.game.layer1_players), 2)
        self.assertEqual(len(self.game.layer2_players), 3)
        self.assertEqual(len(self.game.layer3_players), 0)
        self.assertEqual(self.game.max_bet, 80)
        self.assertEqual(self.game.community_score, 50)
        self.assertEqual(self.game.roles, ['bank', 'odd_setter', 'validator'])

    def test_run_game(self):
        np.random.seed(42)  # Set seed for reproducibility
        layer1_payoffs, layer2_payoffs = self.game.run_game()
        self.assertEqual(len(layer1_payoffs), 2)
        self.assertEqual(len(layer2_payoffs), 3)

    def test_calculate_layer1_payoffs(self):
        bets = [10, 20]
        outcome = True
        payoffs = self.game._calculate_layer1_payoffs(bets, outcome)
        self.assertEqual(payoffs, [30, -20])

    def test_calculate_layer2_payoffs(self):
        bets = [10, 15, 20]
        layer1_outcome = True
        predictions = [True, False, True]
        payoffs = self.game._calculate_layer2_payoffs(bets, layer1_outcome, predictions)
        self.assertEqual(len(payoffs), 3)
        self.assertGreater(payoffs[0], 0)
        self.assertLessEqual(payoffs[1], 0)
        self.assertGreater(payoffs[2], 0)

    def test_update_community_score(self):
        initial_score = self.game.community_score
        self.game.update_community_score([10, 20, 30])
        self.assertNotEqual(self.game.community_score, initial_score)

    def test_update_reputations(self):
        bets = [10, 20, 30, 40, 50]
        payoffs = [15, 25, 35, 45, 55]
        initial_reputations = [player.reputation for player in self.game.layer1_players + self.game.layer2_players]
        self.game.update_reputations(bets, payoffs)
        final_reputations = [player.reputation for player in self.game.layer1_players + self.game.layer2_players]
        self.assertNotEqual(initial_reputations, final_reputations)

    def test_pi_i(self):
        player = self.game.layer1_players[0]
        X = [10, 20, 30, 40, 50]
        payoff = self.game._pi_i(X[0], X, 0)
        self.assertIsInstance(payoff, float)
        self.assertGreater(payoff, 0)

    def test_cost_function(self):
        cost = self.game._cost_function(50)
        self.assertGreater(cost, 0)
        self.assertLess(cost, 50)

    def test_run_game_comprehensive(self):
        np.random.seed(42)  # Set seed for reproducibility
        initial_community_score = self.game.community_score
        initial_reputations = [p.reputation for p in self.game.layer1_players + self.game.layer2_players]
        initial_profits = [p.cumulative_profit for p in self.game.layer1_players + self.game.layer2_players]
        
        layer1_payoffs, layer2_payoffs = self.game.run_game()
        
        self.assertEqual(len(layer1_payoffs), 2)
        self.assertEqual(len(layer2_payoffs), 3)
        
        # Check that community score has changed
        self.assertNotEqual(self.game.community_score, initial_community_score)
        
        # Check that at least one reputation has changed
        final_reputations = [p.reputation for p in self.game.layer1_players + self.game.layer2_players]
        self.assertNotEqual(initial_reputations, final_reputations)
        
        # Check that payoffs were calculated (even if some are zero)
        self.assertEqual(len(layer1_payoffs) + len(layer2_payoffs), len(self.game.layer1_players) + len(self.game.layer2_players))
        
        # Check that at least one non-instigator player has a non-zero payoff
        self.assertTrue(any(payoff != 0 for payoff in layer1_payoffs + layer2_payoffs), "All payoffs are zero")

        # Keep these print statements for debugging
        print("Layer 1 payoffs:", layer1_payoffs)
        print("Layer 2 payoffs:", layer2_payoffs)

        # Check that game state has changed in some way
        self.assertNotEqual(
            (initial_community_score, initial_reputations, initial_profits),
            (self.game.community_score, final_reputations, [p.cumulative_profit for p in self.game.layer1_players + self.game.layer2_players])
        )

    def test_update_community_score_comprehensive(self):
        initial_score = self.game.community_score
        self.game.update_community_score([10, 20, 30, 40, 50])
        self.assertNotEqual(self.game.community_score, initial_score)
        self.assertGreaterEqual(self.game.community_score, 0)
        self.assertLessEqual(self.game.community_score, 100)

if __name__ == '__main__':
    unittest.main()