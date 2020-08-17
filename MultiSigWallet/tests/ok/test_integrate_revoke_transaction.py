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
        # submit transaction
        change_requirement_params = [
            {'name': 'owners_required',
             'type': 'int',
             'value': 3}
        ]
        submit_tx_params = {'destination': str(self._score_address),
                            'method_name': 'set_wallet_owners_required',
                            'params': json.dumps(change_requirement_params),
                            'description': 'change requirements 2 to 3'}

        submit_tx = transaction_call_success(super(), from_=self._operator,
                                             to_=self._score_address,
                                             method='submit_transaction',
                                             params=submit_tx_params,
                                             icon_service=self.icon_service
                                             )

        self.assertEqual(int(True), result['status'])

        # success case: revoke using confirmed wallet owner
        confirmed_owner1 = self._operator
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=confirmed_owner1,
                                          to_=self._score_address,
                                          method='revokeTransaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        # check wallet_owners who has confirmed transaction(should be none)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getConfirmations",
                "params": {"_offset": "0", "_count": "10", "transaction_uid": "0x00"}
            }
        }

        expected_confirm_owners = []
        actual_confirm_owners = self._query(query_request)
        self.assertEqual(expected_confirm_owners, actual_confirm_owners)

        # failure case: revoke using not confirmed wallet owner
        not_confirmed_owner = self._operator
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=not_confirmed_owner,
                                          to_=self._score_address,
                                          method='revokeTransaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(False, result['status'])

        expected_revert_massage = f"{self._operator} has not confirmed to the transaction id '0' yet"
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # failure case: try revoke transaction which is already executed

        # confirm transaction using owner1, 2
        confirmed_owner1 = self._operator
        confirmed_owner2 = self._owner2
        confirm_tx_params = {'transaction_uid': '0x00'}
        confirm_tx1 = transaction_call_success(super(), from_=confirmed_owner1,
                                               to_=self._score_address,
                                               method='confirm_transaction',
                                               params=confirm_tx_params,
                                               icon_service=self.icon_service
                                               )
        confirm_tx_params = {'transaction_uid': '0x00'}
        confirm_tx2 = transaction_call_success(super(), from_=confirmed_owner2,
                                               to_=self._score_address,
                                               method='confirm_transaction',
                                               params=confirm_tx_params,
                                               icon_service=self.icon_service
                                               )
        prev_block, tx_results = self._make_and_req_block([confirm_tx1, confirm_tx2])

        self.assertEqual(True, result['status'])
        self.assertEqual(True, tx_results[1].status)

        # check transaction executed.
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getTransactionsExecuted",
                "params": {"transaction_uid": "0x00"}
            }
        }
        response = self._query(query_request)
        self.assertEqual(True, response)

        # try to revoke confirmation of the transaction which is already executed
        confirmed_owner1 = self._operator
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=confirmed_owner1,
                                          to_=self._score_address,
                                          method='revokeTransaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        expected_revert_massage = "transaction id '0' has already been executed"
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)
