from mathematical_model import Game, GameParameters
import asyncio
from web3 import Web3
import uuid

class LiveStreamGame(Game):
    def __init__(self, params, time_constraint, blockchain_provider, streamer_id, web3_instance=None):
        super().__init__(params, time_constraint)
        if web3_instance is None:
            self.w3 = Web3(Web3.HTTPProvider(blockchain_provider))
        else:
            self.w3 = web3_instance
        self.proposed_actions = {}
        self.live_actions = {}
        self.min_supporters = 3
        self.streamer_id = streamer_id
        self.pending_actions = {}
        self.active_actions = {}
        self.completed_actions = {}

    async def propose_action(self, proposer, action_type, bet_amount):
        action_id = self.generate_action_id()
        self.pending_actions[action_id] = {
            'proposer': proposer,
            'type': action_type,
            'bet': bet_amount,
            'supporters': [],
            'total_bet': bet_amount,
            'is_streamer_action': proposer == self.streamer_id,
            'status': 'pending'
        }
        return action_id

    async def support_action(self, supporter, action_id, bet_amount):
        if action_id in self.pending_actions:
            action = self.pending_actions[action_id]
            action['supporters'].append(supporter)
            action['total_bet'] += bet_amount
            await self.check_action_status(action_id)
        else:
            print(f"Action {action_id} not found in pending actions")

    async def check_action_status(self, action_id):
        if action_id in self.pending_actions:
            action = self.pending_actions[action_id]
            if len(action['supporters']) >= self.min_supporters:
                await self.activate_action(action_id)
        else:
            print(f"Action {action_id} not found in pending actions")

    async def activate_action(self, action_id):
        if action_id in self.pending_actions:
            action = self.pending_actions.pop(action_id)
            action['status'] = 'active'
            self.active_actions[action_id] = action
            await self.execute_action(action_id)
        else:
            print(f"Action {action_id} not found in pending actions")

    async def execute_action(self, action_id):
        if action_id in self.live_actions:
            action = self.live_actions[action_id]

            print(f"Executing action {action_id}")
        else:
            print(f"Action {action_id} not found in live actions")

    async def verify_action(self, action_id, verifier, is_verified):
        if action_id in self.live_actions:
            if is_verified:
                await self.process_payoffs(action_id)
                del self.live_actions[action_id]
            else:
                await self.handle_failed_verification(action_id)
        else:
            print(f"Action {action_id} not found in live actions")

    async def process_payoffs(self, action_id):
        if action_id in self.live_actions:
            action = self.live_actions[action_id]
            payoffs = self._calculate_payoffs(action)
            await self.distribute_payoffs(action_id, payoffs)
        else:
            print(f"Action {action_id} not found in live actions")

    async def distribute_payoffs(self, action_id, payoffs):
        if action_id in self.live_actions:
            action = self.live_actions[action_id]
            if payoffs:
                for player, payoff in zip([action['proposer']] + action['supporters'], payoffs):
                    await self.send_payoff(player, payoff)
            else:
                print(f"No payoffs calculated for action {action_id}")
        else:
            print(f"Action {action_id} not found in live actions")

    async def send_payoff(self, recipient, amount):
        transaction = {
            'to': recipient,
            'value': amount,
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.w3.eth.default_account),
        }
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key='your_private_key_here')
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def generate_action_id(self):
        return str(uuid.uuid4())

    def _calculate_payoffs(self, action):
        return [10] * (len(action['supporters']) + 1)

    async def handle_failed_verification(self, action_id):
        if action_id in self.live_actions:
            del self.live_actions[action_id]
            print(f"Action {action_id} failed verification")
        else:
            print(f"Action {action_id} not found in live actions")

    def get_pending_actions(self):
        return self.pending_actions

    def get_active_actions(self):
        return self.active_actions

    def get_completed_actions(self):
        return self.completed_actions