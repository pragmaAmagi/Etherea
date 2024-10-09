import React, { useState } from 'react';
import styled from 'styled-components';
import { runGame } from '../services/api';

const RunGameContainer = styled.div`
  background-color: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius};
  padding: ${props => props.theme.space.large};
  margin-bottom: ${props => props.theme.space.large};
  box-shadow: ${props => props.theme.boxShadow};
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.secondary};
  margin-bottom: ${props => props.theme.space.medium};
`;

const Select = styled.select`
  margin-right: ${props => props.theme.space.small};
  padding: ${props => props.theme.space.small};
`;

const Button = styled.button`
  background-color: ${props => props.theme.colors.secondary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.space.small} ${props => props.theme.space.medium};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
`;

const Message = styled.p`
  color: ${props => props.success ? props.theme.colors.secondary : props.theme.colors.error};
  margin-top: ${props => props.theme.space.small};
`;

function RunGame({ onGameRun }) {
    const [outcome, setOutcome] = useState('win');
    const [message, setMessage] = useState(null);
    const [updatedState, setUpdatedState] = useState(null);

    const handleRunGame = async () => {
        try {
            const result = await runGame(outcome);
            console.log('Game run result:', result);
            setMessage(`Game run successfully. New community score: ${result.communityScore}`);
            setUpdatedState(result);
            if (onGameRun) onGameRun();
        } catch (error) {
            console.error('Error running game:', error);
            setMessage('Failed to run game. Please try again.');
        }
    };

    return (
        <RunGameContainer>
            <Title>Run Game</Title>
            <Select value={outcome} onChange={(e) => setOutcome(e.target.value)}>
                <option value="win">Win</option>
                <option value="lose">Lose</option>
            </Select>
            <Button onClick={handleRunGame}>Run Game</Button>
            {message && <Message success={message.includes('successfully')}>{message}</Message>}
            {updatedState && (
                <div>
                    <h3>Updated Game State:</h3>
                    <p>Community Score: {updatedState.communityScore}</p>
                    <p>Current Round: {updatedState.currentRound}</p>
                    <p>Active Players: {updatedState.activePlayers}</p>
                    <p>Time Remaining: {updatedState.timeRemaining}</p>
                </div>
            )}
        </RunGameContainer>
    );
}

export default RunGame;