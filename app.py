from flask import Flask, render_template, request, jsonify
from community_betting import CommunityBettingGame

app = Flask(__name__)
game = CommunityBettingGame()

@app.route('/')
def home():
    return render_template('index.html', game_status=game.get_status())

@app.route('/place_bet', methods=['POST'])
def place_bet():
    player = int(request.form['player'])
    amount = float(request.form['amount'])
    success, message = game.place_bet(player, amount)
    return jsonify({'success': success, 'message': message, 'status': game.get_status()})

@app.route('/run_game', methods=['POST'])
def run_game():
    app.logger.info('Run game route called')
    outcome = request.form['outcome'] == 'win'
    app.logger.info(f'Outcome: {outcome}')
    layer1_payoffs, layer2_payoffs = game.run_game(outcome)
    app.logger.info(f'Game run completed. Layer1 payoffs: {layer1_payoffs}, Layer2 payoffs: {layer2_payoffs}')
    return jsonify({
        'layer1_payoffs': layer1_payoffs,
        'layer2_payoffs': layer2_payoffs,
        'status': game.get_status()
    })

@app.route('/reset_game', methods=['POST'])
def reset_game():
    game.reset_game()
    return jsonify({'message': 'Game reset', 'status': game.get_status()})

if __name__ == '__main__':
    app.run(debug=True)