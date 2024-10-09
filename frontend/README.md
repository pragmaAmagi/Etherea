# Etherea

Eltherea is an innovative, web-based multiplayer game that simulates a community-driven betting system with real-time interactions and collaborative decision-making.

# Game Concept

Etherea, players participate in a dynamic betting environment where individual actions impact the community as a whole. The game explores concepts of group dynamics, risk assessment, and collective decision-making in a gamified setting.

Key features of the game include:
- Community Score: A shared metric affected by all players' actions
- Individual Player Metrics: Including reputation and cumulative profit
- Action Proposal and Support System: Players can propose actions and support others' proposals
- Real-time Updates: Game state changes are reflected immediately for all players

# How It Works

1. Players can propose betting actions, specifying an amount and action type.
2. Proposed actions become "pending actions" visible to all players.
3. Other players can view details of pending actions and choose to support them.
4. The game runs in rounds, processing all pending actions and updating the community score and individual player metrics.
5. Players' reputations and profits are updated based on the outcomes of their actions and the overall community performance.

# Technology Stack

- Frontend: React.js with Styled Components for a responsive and visually appealing UI
- Backend: Flask (Python) for game logic and API endpoints
- State Management: React Hooks for efficient state updates
- API Communication: Fetch API for seamless frontend-backend interaction

# Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/Etherea.git
   cd Etherea
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

3. Set up the frontend:
   ```
   cd ../frontend
   npm install
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

# Game Components

- Game State: Displays current community score, round, active players, and time remaining
- Pending Actions: Shows proposed actions awaiting processing
- Propose Action Form: Allows players to submit new action proposals
- Run Game: Processes pending actions and advances the game state
- Reset Game: Resets the game to its initial state

#Contributing

We welcome contributions to the Etherea! Whether it's bug fixes, feature additions, or documentation improvements, please feel free to make a pull request.



