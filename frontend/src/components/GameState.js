import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { getGameState } from '../services/api';

const GameStateContainer = styled.div`
  background-color: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
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

const StateItem = styled.p`
  margin-bottom: ${props => props.theme.space.small};
`;

const RefreshButton = styled.button`
  background-color: ${props => props.theme.colors.secondary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.space.small} ${props => props.theme.space.medium};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  cursor: pointer;
  margin-top: ${props => props.theme.space.medium};

  &:hover {
    opacity: 0.8;
  }
`;

function GameState({ refreshTrigger }) {
  const [gameState, setGameState] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const state = await getGameState();
        setGameState(state);
        setIsLoading(false);
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
      }
    };
    fetchData();
  }, [refreshTrigger]);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!gameState) return <p>No game state available.</p>;

  return (
    <GameStateContainer>
      <Title>Game State</Title>
      <StateItem>Community Score: {gameState.communityScore}</StateItem>
      <StateItem>Current Round: {gameState.currentRound}</StateItem>
      <StateItem>Active Players: {gameState.activePlayers}</StateItem>
      <StateItem>Time Remaining: {gameState.timeRemaining}</StateItem>
    </GameStateContainer>
  );
}

export default GameState;
