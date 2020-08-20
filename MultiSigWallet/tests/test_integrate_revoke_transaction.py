# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from MultiSigWallet.tests.msw_utils import MultiSigWalletTests


class TestIntegrateRevokeTransaction(MultiSigWalletTests):

    def setUp(self):
        super().setUp()

    def test_revoke_transaction(self):
        result = self.set_wallet_owners_required(2)
        txuid_executed = self.get_transaction_created_uid(result)

        # submit transaction
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)

        # success case: revoke using confirmed wallet owner
        result = self.revoke_transaction(txuid)

        # check wallet_owners who has confirmed transaction(should be none)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 0)
        self.assertEqual(transaction['state'], 'CANCELLED')

        # failure case: revoke using not confirmed wallet owner
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)

        result = self.revoke_transaction(txuid, from_=self._owner2, success=False)
        owner2_uid = self.get_wallet_owner_uid(self._owner2.get_address())
        expected_revert_massage = f"TransactionNotConfirmed('TRANSACTION_{txuid}', {owner2_uid})"
        self.assertEqual(expected_revert_massage, result['failure']['message'])

        # failure case: try revoke transaction which is already executed
        transaction = self.get_transaction(txuid_executed)
        self.assertEqual(transaction['state'], 'EXECUTED')

        # try to revoke confirmation of the transaction which is already executed
        result = self.revoke_transaction(txuid_executed, success=False)
        expected_revert_massage = f"InvalidState('TRANSACTION_{txuid_executed}_state_STATEDB', 'EXECUTED', 'WAITING')"
        self.assertEqual(expected_revert_massage, result['failure']['message'])