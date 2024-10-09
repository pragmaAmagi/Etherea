import React from 'react';
import styled from 'styled-components';
import logo from './Etherea Logo.png';  // Update this line

const HeaderContainer = styled.header`
  background-color: ${props => props.theme.colors.appBackground};
  color: ${props => props.theme.colors.background};
  padding: ${props => props.theme.space.large};
  margin-bottom: ${props => props.theme.space.xlarge};
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 2px solid ${props => props.theme.colors.accent1};
`;

const Logo = styled.img`
  width: ${props => props.width || 'auto'};
  height: ${props => props.height || '100px'};
  max-height: ${props => props.maxHeight || '150px'};
  object-fit: contain;
  margin-right: 20px;
`;

const Title = styled.h1`
  font-size: ${props => props.theme.fontSizes.xxlarge};
  margin: 0;
  color: ${props => props.theme.colors.secondary};
  text-shadow: 1px 1px 2px ${props => props.theme.colors.accent3};
`;

function Header() {
    return (
        <HeaderContainer>
            <Logo
                src={logo}  // Update this line
                alt="Etherea Logo"
                height="120px"
                maxHeight="200px"
            />
            <Title>Etherea</Title>
        </HeaderContainer>
    );
}

export default Header;