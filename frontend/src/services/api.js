const API_URL = 'http://localhost:5000';

export const getGameState = () =>
    fetch(`${API_URL}/game_state`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        });

export const getPendingActions = () =>
    fetch(`${API_URL}/pending_actions`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        });

export const proposeAction = (action) =>
    fetch(`${API_URL}/propose_action`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(action),
    })
        .then(res => {
            console.log('Propose action response:', res);
            if (!res.ok) {
                return res.json().then(err => { throw err; });
            }
            return res.json();
        })
        .catch(error => {
            console.error('Error in proposeAction:', error);
            throw error;
        });

export const supportAction = (actionId, support) =>
    fetch(`${API_URL}/support_action/${actionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ support }),
    }).then(res => res.json());

export const runGame = (outcome) =>
    fetch(`${API_URL}/run_game`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ outcome }),
    }).then(res => res.json());

export const resetGame = () =>
    fetch(`${API_URL}/reset_game`, {
        method: 'POST',
    }).then(res => res.json());
