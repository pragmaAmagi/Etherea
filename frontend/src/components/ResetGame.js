import React, { useState } from 'react';
import styled from 'styled-components';
import { resetGame } from '../services/api';

const ResetButton = styled.button`
  background-color: ${props => props.theme.colors.error};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.space.small} ${props => props.theme.space.medium};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  cursor: pointer;
  margin-top: ${props => props.theme.space.large};

  &:hover {
    opacity: 0.8;
  }
`;

const Message = styled.p`
  color: ${props => props.success ? props.theme.colors.secondary : props.theme.colors.error};
  margin-top: ${props => props.theme.space.small};
`;

function ResetGame({ onGameReset }) {
    const [message, setMessage] = useState(null);

    const handleResetGame = async () => {
        try {
            const result = await resetGame();
            console.log('Game reset result:', result);
            setMessage('Game reset successfully');
            if (onGameReset) onGameReset();  // Call the refresh function
        } catch (error) {
            console.error('Error resetting game:', error);
            setMessage('Failed to reset game. Please try again.');
        }
    };

    return (
        <div>
            <ResetButton onClick={handleResetGame}>Reset Game</ResetButton>
            {message && <Message success={message.includes('successfully')}>{message}</Message>}
        </div>
    );
}

export default ResetGame;