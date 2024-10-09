import React, { useState, useCallback } from 'react';
import { ThemeProvider } from 'styled-components';
import theme from './styles/theme';
import GlobalStyle from './styles/GlobalStyle';
import Header from './components/Header';
import GameState from './components/GameState';
import PendingActions from './components/PendingActions';
import ProposeActionForm from './components/ProposeActionForm';
import RunGame from './components/RunGame';
import ResetGame from './components/ResetGame';
import styled from 'styled-components';

const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const MainContent = styled.main`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Sidebar = styled.aside`
  background-color: ${props => props.theme.colors.componentBackground};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius};
  padding: ${props => props.theme.space.large};
  box-shadow: ${props => props.theme.boxShadow};
`;

function App() {
  const [gameStateRefreshKey, setGameStateRefreshKey] = useState(0);
  const [pendingActionsRefreshKey, setPendingActionsRefreshKey] = useState(0);

  const refreshGameState = useCallback(() => {
    setGameStateRefreshKey(prevKey => prevKey + 1);
  }, []);

  const refreshPendingActions = useCallback(() => {
    setPendingActionsRefreshKey(prevKey => prevKey + 1);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AppContainer>
        <Header />
        <MainContent>
          <div>
            <GameState key={gameStateRefreshKey} />
            <PendingActions key={pendingActionsRefreshKey} />
          </div>
          <Sidebar>
            <ProposeActionForm onPendingActionsUpdated={refreshPendingActions} />
            <RunGame onGameRun={refreshGameState} />
            <ResetGame onGameReset={() => {
              refreshGameState();
              refreshPendingActions();
            }} />
          </Sidebar>
        </MainContent>
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;