import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { getPendingActions, supportAction } from '../services/api';

const PendingActionsContainer = styled.div`
  background-color: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.white};
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

const Action = styled.div`
  background-color: ${props => props.theme.colors.primary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius};
  padding: ${props => props.theme.space.medium};
  margin-bottom: ${props => props.theme.space.medium};
`;

const ViewDetailsButton = styled.button`
  background-color: ${props => props.theme.colors.secondary};
  color: ${props => props.theme.colors.primary};
  padding: ${props => props.theme.space.small} ${props => props.theme.space.medium};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  cursor: pointer;
  margin-top: ${props => props.theme.space.small};

  &:hover {
    opacity: 0.8;
  }
`;

const ActionDetails = styled.div`
  background-color: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius};
  padding: ${props => props.theme.space.medium};
  margin-top: ${props => props.theme.space.small};
`;

const CloseButton = styled.button`
  background-color: ${props => props.theme.colors.error};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.space.small};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  cursor: pointer;
  float: right;

  &:hover {
    opacity: 0.8;
  }
`;

const ActionTitle = styled.h3`
  color: ${props => props.theme.colors.white};
  margin-bottom: ${props => props.theme.space.small};
`;

const PlayerInfo = styled.div`
  margin-top: ${props => props.theme.space.small};
  font-size: 0.9em;
`;

function PendingActions() {
  const [pendingActions, setPendingActions] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedActionId, setExpandedActionId] = useState(null);

  const fetchPendingActions = () => {
    setIsLoading(true);
    getPendingActions()
      .then(actions => {
        console.log('Fetched pending actions:', actions);
        setPendingActions(actions);
        setError(null);
      })
      .catch(err => {
        console.error('Error fetching pending actions:', err);
        setError(`Failed to fetch pending actions. Error: ${err.message}`);
      })
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchPendingActions();
  }, []);

  const handleSupport = async (actionId) => {
    try {
      await supportAction(actionId, true);
      fetchPendingActions();  // Refresh the list after supporting
    } catch (err) {
      console.error('Error supporting action:', err);
      setError('Failed to support action. Please try again.');
    }
  };

  const toggleActionDetails = (actionId) => {
    setExpandedActionId(expandedActionId === actionId ? null : actionId);
  };

  if (isLoading) return <p>Loading pending actions...</p>;
  if (error) return <p>Error: {error}</p>;
  if (pendingActions.length === 0) return <p>No pending actions available.</p>;

  return (
    <PendingActionsContainer>
      <Title>Pending Actions</Title>
      {pendingActions.map(action => (
        <Action key={action.player_index}>
          <ActionTitle>Bet by Player {action.player_index}</ActionTitle>
          <p>Amount: {action.amount}</p>
          <p>Alignment: {action.alignment.toFixed(2)}</p>
          <ViewDetailsButton onClick={() => toggleActionDetails(action.player_index)}>
            {expandedActionId === action.player_index ? 'Hide Details' : 'View Details'}
          </ViewDetailsButton>
          {expandedActionId === action.player_index && (
            <PlayerInfo>
              <p>Player Reputation: {action.reputation.toFixed(2)}</p>
              <p>Cumulative Profit: {action.cumulative_profit.toFixed(2)}</p>
            </PlayerInfo>
          )}
        </Action>
      ))}
    </PendingActionsContainer>
  );
}

export default PendingActions;
