from community_betting import CommunityBettingGame

def main():
    print("Welcome to the Community Betting Game!")
    game = CommunityBettingGame()
    
    print(f"This game has {len(game.game.layer1_players)} Layer 1 players and {len(game.game.layer2_players)} Layer 2 players.")
    print(f"Valid player numbers are 0 to {len(game.game.layer1_players) + len(game.game.layer2_players) - 1}.")
    
    while True:
        command = input("Enter a command (start/bet/run/status/quit): ")
        if command == "start":
            game.reset_game()
            print("New game started!")
        elif command.startswith("bet"):
            parts = command.split()
            if len(parts) == 3:
                try:
                    _, player, amount = parts
                    success, message = game.place_bet(int(player), float(amount))
                    print(message)
                except ValueError:
                    print("Invalid bet command. Player and amount must be numbers.")
            else:
                print("Invalid bet command. Use format: bet <player_number> <amount>")
        elif command == "run":
            layer1_outcome_input = input("Enter the Layer 1 outcome (win/loss): ").lower()
            if layer1_outcome_input in ['win', 'loss']:
                layer1_outcome = layer1_outcome_input == 'win'
                layer1_payoffs, layer2_payoffs = game.run_game(layer1_outcome)
                print(f"Layer 1 outcome: {'Win' if layer1_outcome else 'Loss'}")
                print("Layer 1 payoffs:", layer1_payoffs)
                print("Layer 2 payoffs:", layer2_payoffs)
            else:
                print("Invalid input. Please enter 'win' or 'loss'.")
        elif command == "status":
            status = game.get_status()
            print(f"Community Score: {status['community_score']}")
            for player in status['players']:
                print(f"Player {player['id']}: Bet = {player['bet']}, Reputation = {player['reputation']:.2f}, Cumulative Profit = {player['cumulative_profit']:.2f}")
        elif command == "quit":
            break
        else:
            print("Invalid command. Try again.")

if __name__ == "__main__":
    main()