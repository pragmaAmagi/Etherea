import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from live_stream_game import LiveStreamGame
from mathematical_model import GameParameters

class TestLiveStreamGame(unittest.TestCase):

    def setUp(self):
        params = GameParameters()
        self.mock_w3 = Mock()
        self.mock_w3.eth.gas_price = 20000000000
        self.mock_w3.eth.get_transaction_count.return_value = 0
        self.mock_w3.eth.account.sign_transaction.return_value.rawTransaction = b'raw_transaction'
        self.mock_w3.eth.send_raw_transaction.return_value = b'transaction_hash'
        self.mock_w3.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        
        # Make wait_for_transaction_receipt a regular method, not a coroutine
        self.mock_w3.eth.wait_for_transaction_receipt = Mock(return_value={'status': 1})

        self.game = LiveStreamGame(params, time_constraint=100, blockchain_provider='http://localhost:8545', streamer_id='streamer1', web3_instance=self.mock_w3)

    def test_propose_action(self):
        action_id = asyncio.run(self.game.propose_action('player1', 'bet', 10))
        self.assertIsNotNone(action_id)
        self.assertIn(action_id, self.game.proposed_actions)
        action = self.game.proposed_actions[action_id]
        self.assertEqual(action['proposer'], 'player1')
        self.assertEqual(action['type'], 'bet')
        self.assertEqual(action['bet'], 10)
        self.assertEqual(action['total_bet'], 10)
        self.assertEqual(len(action['supporters']), 0)
        self.assertFalse(action['is_streamer_action'])

    def test_propose_action_by_streamer(self):
        action_id = asyncio.run(self.game.propose_action(self.game.streamer_id, 'bet', 10))
        self.assertIsNotNone(action_id)
        self.assertIn(action_id, self.game.proposed_actions)
        action = self.game.proposed_actions[action_id]
        self.assertTrue(action['is_streamer_action'])

    def test_support_action(self):
        action_id = asyncio.run(self.game.propose_action('player1', 'bet', 10))
        asyncio.run(self.game.support_action('player2', action_id, 5))
        action = self.game.proposed_actions[action_id]
        self.assertEqual(len(action['supporters']), 1)
        self.assertEqual(action['total_bet'], 15)

    @patch('live_stream_game.LiveStreamGame.activate_action')
    def test_check_action_status(self, mock_activate):
        action_id = asyncio.run(self.game.propose_action('player1', 'bet', 10))
        for i in range(3):
            asyncio.run(self.game.support_action(f'player{i+2}', action_id, 5))
        mock_activate.assert_called_once()

    def test_activate_action(self):
        asyncio.run(self._test_activate_action())

    async def _test_activate_action(self):
        action_id = await self.game.propose_action('player1', 'bet', 10)
        await self.game.activate_action(action_id)
        self.assertIn(action_id, self.game.live_actions)
        self.assertNotIn(action_id, self.game.proposed_actions)

    def test_verify_action(self):
        asyncio.run(self._test_verify_action())

    async def _test_verify_action(self):
        action_id = await self.game.propose_action('player1', 'bet', 10)
        await self.game.activate_action(action_id)
        
        await self.game.verify_action(action_id, 'verifier1', True)
        self.assertNotIn(action_id, self.game.live_actions)
        
        # Test for non-existent action
        await self.game.verify_action('non_existent_id', 'verifier2', False)
        # Add assertion to check if proper message is printed

    def test_process_payoffs(self):
        asyncio.run(self._test_process_payoffs())

    async def _test_process_payoffs(self):
        action_id = await self.game.propose_action('player1', 'bet', 10)
        await self.game.support_action('player2', action_id, 5)
        await self.game.activate_action(action_id)
        
        with patch.object(self.game, '_calculate_payoffs', return_value=[20, 10]):
            await self.game.process_payoffs(action_id)
        
        # Test for non-existent action
        await self.game.process_payoffs('non_existent_id')
        # Add assertion to check if proper message is printed

    def test_distribute_payoffs(self):
        asyncio.run(self._test_distribute_payoffs())

    async def _test_distribute_payoffs(self):
        action_id = await self.game.propose_action('player1', 'bet', 10)
        await self.game.support_action('player2', action_id, 5)
        await self.game.activate_action(action_id)
        
        with patch.object(self.game, 'send_payoff') as mock_send_payoff:
            await self.game.distribute_payoffs(action_id, [20, 10])
            self.assertEqual(mock_send_payoff.call_count, 2)
        
        # Test for non-existent action
        await self.game.distribute_payoffs('non_existent_id', [10, 10])
        # Add assertion to check if proper message is printed

    def test_send_payoff(self):
        asyncio.run(self._test_send_payoff())

    async def _test_send_payoff(self):
        receipt = await self.game.send_payoff('0x742d35Cc6634C0532925a3b844Bc454e4438f44e', 100)
        self.mock_w3.eth.account.sign_transaction.assert_called_once()
        self.mock_w3.eth.send_raw_transaction.assert_called_once()
        self.mock_w3.eth.wait_for_transaction_receipt.assert_called_once()
        self.assertEqual(receipt, {'status': 1})

    def test_generate_action_id(self):
        action_id1 = self.game.generate_action_id()
        action_id2 = self.game.generate_action_id()
        self.assertNotEqual(action_id1, action_id2)

    def test_calculate_payoffs(self):
        action = {
            'proposer': 'player1',
            'supporters': ['player2', 'player3']
        }
        payoffs = self.game._calculate_payoffs(action)
        self.assertEqual(len(payoffs), 3)
        self.assertTrue(all(payoff == 10 for payoff in payoffs))

    def test_handle_failed_verification(self):
        asyncio.run(self._test_handle_failed_verification())

    async def _test_handle_failed_verification(self):
        action_id = await self.game.propose_action('player1', 'bet', 10)
        await self.game.activate_action(action_id)
        await self.game.handle_failed_verification(action_id)
        self.assertNotIn(action_id, self.game.live_actions)

    def test_full_game_simulation(self):
        asyncio.run(self._test_full_game_simulation())

    async def _test_full_game_simulation(self):
        with patch.object(self.game, 'run_game', return_value=([10, 20], [30, 40, 50])):
            action_id = await self.game.propose_action('player1', 'bet', 10)
            await self.game.support_action('player2', action_id, 5)
            await self.game.support_action('player3', action_id, 5)
            await self.game.support_action('player4', action_id, 5)
            await self.game.verify_action(action_id, 'verifier1', True)
        
        self.assertNotIn(action_id, self.game.proposed_actions)
        self.assertNotIn(action_id, self.game.live_actions)
        self.mock_w3.eth.account.sign_transaction.assert_called()
        self.mock_w3.eth.send_raw_transaction.assert_called()
        self.mock_w3.eth.wait_for_transaction_receipt.assert_called()

if __name__ == '__main__':
    unittest.main()