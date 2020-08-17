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

import json


class TestIntegrateSendToken(MultiSigWalletTests):

    def setUp(self):
        super().setUp()

    def test_send_token(self):
        # success case: send 500 token to owner4
        # deposit owner1's 1000 token to multisig wallet score
        transfer_tx_params = {'_to': str(self._score_address), '_value': str(hex(1000))}
        result = transaction_call_success(super(), from_=self._operator,
                                          addr_to=self._irc2_address,
                                          method='transfer',
                                          params=transfer_tx_params,
                                          icon_service=self.icon_service)

        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

        # check multisig wallet score's token amount(should be 1000)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._score_address)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(1000, response)

        # check owner4's token amount(should be 0)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._owner4)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(0, response)

        # make transaction which send 500 token to owner4
        transfer_token_params = [
            {'name': '_to',
             'type': 'Address',
             'value': str(self._owner4)},
            {'name': '_value',
             'type': 'int',
             'value': 500}
        ]

        # submit transaction
        submit_tx_params = {'destination': str(self._irc2_address),
                            'method_name': 'transfer',
                            'params': json.dumps(transfer_token_params),
                            'description': 'send 500 token to owner4'}

        result = transaction_call_success(super(), from_=self._operator,
                                          to_=self._score_address,
                                          method='submit_transaction',
                                          params=submit_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

        # check confirmation count(should be 1)
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
        expected_confirm_count = 1
        self.assertEqual(response, expected_confirm_count)

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

        # check confirmation count(should be 2)
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
        self.assertEqual(2, response)

        # check owner4's token amount(should be 500)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._owner4)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(500, response)

        # check multisig wallet's token amount(should be 500)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._score_address)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(500, response)

    def test_send_token_revert(self):
        # failure case: raise revert while sending 500 token to owner4.(500 token should not be sended)
        # deposit owner1's 1000 token to multisig wallet score
        transfer_tx_params = {'_to': str(self._score_address), '_value': str(hex(1000))}
        result = transaction_call_success(super(), from_=self._operator,
                                          addr_to=self._irc2_address,
                                          method='transfer',
                                          params=transfer_tx_params,
                                          icon_service=self.icon_service)

        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

        # check multisig wallet score's token amount(should be 1000)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._score_address)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(1000, response)

        # check owner4's token amount(should be 0)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._owner4)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(0, response)

        # make transaction which send 500 token to owner4(call revert_check method)
        revert_check_params = [
            {'name': '_to',
             'type': 'Address',
             'value': str(self._owner4)},
            {'name': '_value',
             'type': 'int',
             'value': 500}
        ]

        # submit transaction
        submit_tx_params = {'destination': str(self._irc2_address),
                            'method_name': 'revert_check',
                            'params': json.dumps(revert_check_params),
                            'description': 'send 500 token to owner4'}

        result = transaction_call_success(super(), from_=self._operator,
                                          to_=self._score_address,
                                          method='submit_transaction',
                                          params=submit_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(int(True), result['status'])

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

        # check confirmation count(should be 2)
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
        self.assertEqual(2, response)

        # check transaction executed count(should be False)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getTransactionsExecuted",
                "params": {'transaction_uid': "0x00"}
            }
        }
        response = self._query(query_request)
        self.assertEqual(False, response)

        # check owner4's token amount(should be 0)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._owner4)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(0, response)

        # check multisig wallet's token amount(should be 1000)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._irc2_address,
            "dataType": "call",
            "data": {
                "method": "balanceOf",
                "params": {'_owner': str(self._score_address)}
            }
        }
        response = self._query(query_request)
        self.assertEqual(1000, response)
