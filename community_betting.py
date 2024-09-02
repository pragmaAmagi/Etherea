import logging
import numpy as np  # Add this line
from mathematical_model import GameParameters, Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommunityBettingGame:
    def __init__(self, config=None):
        self.config = config or {}
        self.game = self._create_game()

    def _create_game(self):
        params = GameParameters(**self.config)
        return Game(params, time_constraint=self.config.get('time_constraint', 10))

    def place_bet(self, player_index, amount):
        total_players = len(self.game.layer1_players) + len(self.game.layer2_players)
        if player_index < 0 or player_index >= total_players:
            logger.warning(f"Invalid player index: {player_index}")
            return False, f"Invalid player number. Please choose a player between 0 and {total_players - 1}."
        
        if player_index < len(self.game.layer1_players):
            player = self.game.layer1_players[player_index]
        else:
            player = self.game.layer2_players[player_index - len(self.game.layer1_players)]
        
        player.place_bet(amount)
        alignment = self.evaluate_bet_alignment(amount)
        logger.info(f"Player {player_index} placed a bet of {amount} with alignment score {alignment:.2f}")
        return True, f"Player {player_index} placed a bet of {amount}. Alignment with community: {alignment:.2f}"

    def evaluate_bet_alignment(self, bet):
        avg_bet = np.mean([player.bet for player in self.game.layer1_players + self.game.layer2_players])
        alignment = 1 - abs(bet - avg_bet) / self.game.max_bet
        return alignment

    def run_game(self, layer1_outcome):
        # Ensure all layer2 players have made a prediction
        for player in self.game.layer2_players:
            if player.prediction is None:
                player.make_prediction(np.random.choice([True, False]))

        layer1_payoffs = self.game._calculate_layer1_payoffs([player.bet for player in self.game.layer1_players], layer1_outcome)
        
        layer2_predictions = [player.prediction for player in self.game.layer2_players]
        layer2_payoffs = self.game._calculate_layer2_payoffs([player.bet for player in self.game.layer2_players], layer1_outcome, layer2_predictions)
        
        self.game.update_community_score([player.bet for player in self.game.layer1_players + self.game.layer2_players])
        self.game.update_reputations([player.bet for player in self.game.layer1_players + self.game.layer2_players], layer1_payoffs + layer2_payoffs)
        self.game.update_cumulative_profits(layer1_payoffs + layer2_payoffs)
        
        logger.info(f"Game run completed. Layer 1 outcome: {'Win' if layer1_outcome else 'Loss'}")
        return layer1_payoffs, layer2_payoffs

    def get_status(self):
        status = {
            "community_score": self.game.community_score,
            "players": []
        }
        for i, player in enumerate(self.game.layer1_players + self.game.layer2_players):
            status["players"].append({
                "id": i,
                "bet": player.bet,
                "reputation": player.reputation,
                "cumulative_profit": player.cumulative_profit
            })
        return status

    def reset_game(self):
        self.game = self._create_game()
        logger.info("Game reset")