# Synergy-Strategy-Algorithm
#Copyright (c) [2024] ACME Media Limited
#All rights reserved.
#Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without fee is hereby granted,
#provided that the above copyright notice appear in all copies and that both the copyright notice and this permission notice appear in supporting documentation, 
#and that the name of ACMe Media Limited not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

#ACME Media Limited DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, 
#IN NO EVENT SHALL ACME Media Limited BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
#LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


# Purpose:
The game is designed to combine:
1.	Evolutionary game theory related to group foraging to reduce greed
2.	Evolutionary stable strategies to encourage positive betting behavior
3.	A non-zero sum game with no house edge
4.	A core that is totally unpredictable with incomplete information
5.	Time constraints agreed upon by the two core players
The game aims to benefit everyone while maintaining unpredictability and incomplete information.

# Mathematical Proof for the Game:

π_i(x_i, X_{-i}) = μ(X)/n - c_i(x_i) + (1-exp(-α * ∑_i x_i)) * x_i * ∑_{j≠i} (x_j / σ_j^2) / (∑_{k≠i} 1/σ_k^2)
Var[π_i] = σ^2(X)/n^2

Updated payoff function 08/18/2024:
π_i(x_i, X_{-i}) = μ(X)/n - c_i(x_i) + (1-exp(-α * ∑_i x_i)) * x_i * ∑_{j≠i} (x_j / σ_j^2) / (∑_{k≠i} 1/σ_k^2) - β * (μ(X) - x_i)^2


π_i(xi, X{-i}): Payoff function for player i
xi: Strategy of player i 
X{-i}: Strategies of all players except i 
μ(X): Mean function of all strategies 
n: Number of players 
c_i(x_i): Cost function for player i 
α: A parameter to assess risk
σ_j: Standard deviation associated with player j

penalty_term(x_i, X) = β * (μ(X) - x_i)^2

β: Penalty coefficient
μ(X): Average bet of all players
x_i: Player i's bet


Game Goals:
  Engaging and Profitable
  Reduction of Greed
  Positive Betting Behavior
  Non-Zero Sum
  Time Contraints


1.	Core Game:
•	Two players
•	50/50 chance outcome (like a coin flip)
•	2x2 payoff matrix
•	Non-zero sum (players can both gain or lose)
•	Mixed strategy equilibrium

B: Heads    B: Tails
A: Heads  (3,3)      (-1,4)
A: Tails  (4,-1)     (2,2)

	(Heads, Heads): 5/9 * 5/9 = 25/81 ≈ 30.86%
(Heads, Tails): 5/9 * 4/9 = 20/81 ≈ 24.69%
(Tails, Heads): 4/9 * 5/9 = 20/81 ≈ 24.69%
(Tails, Tails): 4/9 * 4/9 = 16/81 ≈ 19.75%


2.	Betting Layer:
•	Three spectators betting on the outcome
•	Sealed bid auction format
•	Repeated Game
• Randomly assigned house roles for dispute resolution


3.	Dispute Resolution:
•	If core players disagree on the outcome
•	Two of the three spectators validate the payout

4. Spectator Roles: Instead of betting, the three spectators (X, Y, and Z) will collectively act as the house.
Their roles will be: 
a) Odds Setter: One spectator randomly chosen to set the odds for each outcome. 
b) Banker: One spectator randomly chosen to manage the payouts. 
c) Validator: One spectator left to act as a tie-breaker in case of disputes.

Banking: The Banker would need to have a pool of funds to cover potential payouts. This could be provided equally by all three spectators, or could be backed by an external source.
Validation: The Validator's role is crucial in case A and B disagree on the outcome. They would make the final call, which adds an interesting dynamic as they might be incentivized to rule in favor of the outcome that's most profitable for the house.
Incentives: To align incentives, the spectators could share in the profits (or losses) of the house. This would encourage the Odds Setter to set fair but profitable odds, the Banker to manage payouts correctly, and the Validator to make accurate judgments.

5.	Information Structure:
•	Imperfect information
