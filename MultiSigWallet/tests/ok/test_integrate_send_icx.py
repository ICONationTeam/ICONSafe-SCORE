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

from MultiSigWallet.tests.msw_utils import MultiSigWalletTests

ICX_FACTOR = 10 ** 18


class TestIntegrateSendIcx(MultiSigWalletTests):

    def setUp(self):
        super().setUp()

    def deposit_icx_to_multisig_score(self, value: int):
        send_icx_value = value
        icx_send_tx = self._make_icx_send_tx(self._genesis,
                                             self._score_address,
                                             send_icx_value)

        prev_block, tx_results = self._make_and_req_block([icx_send_tx])

        self.assertEqual(result['status'], int(True))

        # check if icx is deposited to multisig wallet successfully
        query_request = {
            "address": self._score_address
        }
        response = self._query(query_request, 'icx_getBalance')
        self.assertEqual(send_icx_value, response)

    def test_send_icx_negative_value(self):
        # failure case: submit transaction which send -10 icx to token score
        submit_tx_params = {'destination': str(self._irc2_address),
                            'description': 'send negative icx value',
                            '_value': f'{hex(-10*ICX_FACTOR)}'}

        submit_tx = transaction_call_success(super(), from_=self._operator,
                                             to_=self._score_address,
                                             method='submit_transaction',
                                             params=submit_tx_params,
                                             icon_service=self.icon_service
                                             )

        self.assertEqual(result['status'], int(False))

        expected_revert_massage = 'only positive number is accepted'
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

    def test_send_icx_to_score(self):
        # success case: send icx to SCORE(token score)

        # deposit 100 icx to wallet SCORE
        send_icx_value = 100 * ICX_FACTOR
        self.deposit_icx_to_multisig_score(send_icx_value)

        # submit transaction which send 10 icx to token score
        submit_tx_params = {'destination': str(self._irc2_address),
                            'description': 'send 10 icx to token score',
                            '_value': f'{hex(10*ICX_FACTOR)}'}

        submit_tx = transaction_call_success(super(), from_=self._operator,
                                             to_=self._score_address,
                                             method='submit_transaction',
                                             params=submit_tx_params,
                                             icon_service=self.icon_service
                                             )

        self.assertEqual(result['status'], int(True))

        # check token score icx (should be 0)
        query_request = {
            "address": self._irc2_address
        }
        response = self._query(query_request, "icx_getBalance")
        self.assertEqual(response, 0)

        # confirm transaction
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=self._owner2,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

        # check getConfirmationCount(should be 2)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getConfirmationCount",
                "params": {'transaction_uid': "0x00"}
            }
        }
        response = self._query(query_request)
        expected_confirm_count = 2
        self.assertEqual(response, expected_confirm_count)

        # check the token score address' icx
        query_request = {
            "address": self._irc2_address
        }

        expected_token_score_icx = 10 * ICX_FACTOR
        actual_token_score_icx = self._query(query_request, "icx_getBalance")
        self.assertEqual(expected_token_score_icx, actual_token_score_icx)

        # check multisig wallet score's icx(should be 90)
        query_request = {
            "address": self._score_address
        }
        response = self._query(query_request, "icx_getBalance")
        self.assertEqual(90 * ICX_FACTOR, response)

        # failure case: when confirming to already executed transaction,
        # transaction shouldn't be executed again.
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=self._owner3,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

        # check the token score address' icx
        query_request = {
            "address": self._irc2_address
        }

        expected_token_score_icx = 10 * ICX_FACTOR
        actual_token_score_icx = self._query(query_request, "icx_getBalance")
        self.assertEqual(expected_token_score_icx, actual_token_score_icx)

        # check multisig wallet score's icx(should be 90)
        query_request = {
            "address": self._score_address
        }
        response = self._query(query_request, "icx_getBalance")
        self.assertEqual(90 * ICX_FACTOR, response)

    def test_send_icx_to_eoa(self):
        # success case: send icx to eoa(owner4)

        # deposit 100 icx to wallet SCORE
        send_icx_value = 100 * ICX_FACTOR
        self.deposit_icx_to_multisig_score(send_icx_value)

        # submit transaction which send 10 icx to owner4
        submit_tx_params = {'destination': str(self._owner4),
                            'description': 'send 10 icx to owner4',
                            '_value': f'{hex(10*ICX_FACTOR)}'}

        submit_tx = transaction_call_success(super(), from_=self._operator,
                                             to_=self._score_address,
                                             method='submit_transaction',
                                             params=submit_tx_params,
                                             icon_service=self.icon_service
                                             )

        self.assertEqual(result['status'], int(True))

        # check token owner4 (should be 0)
        query_request = {
            "address": self._owner4
        }
        response = self._query(query_request, "icx_getBalance")
        self.assertEqual(response, 0)

        # confirm transaction
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=self._owner2,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

        # check getConfirmationCount(should be 2)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getConfirmationCount",
                "params": {'transaction_uid': "0x00"}
            }
        }
        response = self._query(query_request)
        expected_confirm_count = 2
        self.assertEqual(response, expected_confirm_count)

        # check the owner4's icx
        query_request = {
            "address": self._owner4
        }

        expected_owner4_icx = 10 * ICX_FACTOR
        actual_owner4_icx = self._query(query_request, "icx_getBalance")
        self.assertEqual(expected_owner4_icx, actual_owner4_icx)

        # check multisig wallet score's icx(should be 90)
        query_request = {
            "address": self._score_address
        }
        response = self._query(query_request, "icx_getBalance")
        self.assertEqual(90 * ICX_FACTOR, response)
