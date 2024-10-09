from flask import Flask, jsonify, request
from flask_cors import CORS
from community_betting import CommunityBettingGame  

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000", "methods": ["GET", "POST", "OPTIONS"]}})  

game = CommunityBettingGame()

# Global game state
game_state = {
    'communityScore': 100,
    'currentRound': 1,
    'activePlayers': 5,
    'timeRemaining': '5:00'
}

pending_actions = []
action_history = []

@app.route('/', methods=['GET'])
def home():
    return "Hello from the Live Synergy Game server!"

@app.route('/game_state', methods=['GET'])
def get_game_state():
    return jsonify(game_state)

@app.route('/pending_actions', methods=['GET'])
def get_pending_actions():
    pending_actions = game.get_pending_actions()
    return jsonify(pending_actions)

@app.route('/propose_action', methods=['POST'])
def propose_action():
    action = request.json
    success, message = game.place_bet(action['player_index'], action['amount'])
    if success:
        return jsonify({"message": message}), 201
    else:
        return jsonify({"error": message}), 400

@app.route('/support_action/<int:action_id>', methods=['POST'])
def support_action(action_id):
    action = next((a for a in pending_actions if a['id'] == action_id), None)
    if action:
        action['supporters'] = action.get('supporters', 0) + 1
        return jsonify(action)
    return jsonify({'error': 'Action not found'}), 404

@app.route('/run_game', methods=['POST'])
def run_game():
    global game_state, pending_actions, action_history
    outcome = request.json.get('outcome')
    
    # Process all pending actions
    for action in pending_actions:
        if action['actionType'] == 'bet':
            game_state['communityScore'] += action['betAmount'] if outcome == 'win' else -action['betAmount']
    
    # Update game state
    game_state['currentRound'] += 1
    game_state['timeRemaining'] = '5:00'  # Reset time for next round
    
    # Move pending actions to history
    action_history.extend(pending_actions)
    pending_actions = []
    
    return jsonify(game_state)

@app.route('/reset_game', methods=['POST'])
def reset_game():
    global game_state, pending_actions, action_history
    game_state = {
        'communityScore': 100,
        'currentRound': 1,
        'activePlayers': 5,
        'timeRemaining': '5:00'
    }
    pending_actions = []
    action_history = []
    return jsonify({'message': 'Game reset successfully'})

@app.route('/api/port', methods=['GET'])
def get_port():
    return jsonify({'port': current_app.config['PORT']})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)