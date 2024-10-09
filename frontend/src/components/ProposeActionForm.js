import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { proposeAction } from '../services/api';

const FormContainer = styled.div`
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

const Form = styled.form`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  margin-bottom: ${props => props.theme.space.small};
  color: ${props => props.theme.colors.text};
`;

const Input = styled.input`
  margin-bottom: ${props => props.theme.space.medium};
  padding: ${props => props.theme.space.small};
  border: 1px solid ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius};
`;

const Select = styled.select`
  margin-bottom: ${props => props.theme.space.medium};
  padding: ${props => props.theme.space.small};
  border: 1px solid ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius};
`;

const SubmitButton = styled.button`
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

function ProposeActionForm({ onPendingActionsUpdated }) {
  const [actionTitle, setActionTitle] = useState('');
  const [actionType, setActionType] = useState('');
  const [betAmount, setBetAmount] = useState('');
  const [isFormValid, setIsFormValid] = useState(false);

  useEffect(() => {
    setIsFormValid(actionTitle !== '' && actionType !== '' && betAmount !== '');
  }, [actionTitle, actionType, betAmount]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Attempting to submit form:', { actionTitle, actionType, betAmount });
    try {
      const response = await proposeAction({
        player_index: 0,  // You might want to dynamically set this
        amount: parseInt(betAmount)
      });
      console.log('Propose action response:', response);
      setActionTitle('');
      setActionType('');
      setBetAmount('');
      if (onPendingActionsUpdated) {
        onPendingActionsUpdated();
      }
    } catch (error) {
      console.error('Error proposing action:', error);
    }
  };

  return (
    <FormContainer>
      <Title>Propose Action</Title>
      <Form onSubmit={handleSubmit}>
        <Label htmlFor="actionTitle">Action Title:</Label>
        <Input
          type="text"
          id="actionTitle"
          value={actionTitle}
          onChange={(e) => setActionTitle(e.target.value)}
          required
        />
        <Label htmlFor="actionType">Action Type:</Label>
        <Select
          id="actionType"
          value={actionType}
          onChange={(e) => setActionType(e.target.value)}
          required
        >
          <option value="">Select an action type</option>
          <option value="bet">Bet</option>
          <option value="fold">Fold</option>
          {/* Add more action types as needed */}
        </Select>
        <Label htmlFor="betAmount">Bet Amount:</Label>
        <Input
          type="number"
          id="betAmount"
          value={betAmount}
          onChange={(e) => setBetAmount(e.target.value)}
          min="0"
          required
        />
        <SubmitButton type="submit" disabled={!isFormValid}>
          Propose Action
        </SubmitButton>
      </Form>
    </FormContainer>
  );
}

export default ProposeActionForm;
