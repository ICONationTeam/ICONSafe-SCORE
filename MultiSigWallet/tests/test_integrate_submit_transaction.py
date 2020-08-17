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
from MultiSigWallet.tests.utils import *


class TestIntegrateSubmitTransaction(MultiSigWalletTests):

    def setUp(self):
        super().setUp()

    def test_submit_transaction_validate_params_format(self):

        # success case: valid params format
        self.change_req_to(2)

        # failure case: when type and value's actual type is not match, should be revert.
        not_match_type_params = [
            {'name': 'owners_required',
             'type': 'bool',
             'value': "521"}
        ]
        submit_tx_params = {'destination': str(self._score_address),
                            'method_name': 'set_wallet_owners_required',
                            'params': json.dumps(not_match_type_params),
                            'description': 'change requirements 2 to 3'}

        result = transaction_call_error(super(), from_=self._operator,
                                        to_=self._score_address,
                                        method='submit_transaction',
                                        params=submit_tx_params,
                                        icon_service=self.icon_service
                                        )
        expected_revert_massage = "Cannot convert 521 from type bool"
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # failure case: when input unsupported type as params' type
        unsupported_type_params = [
            {'name': 'owners_required',
             'type': 'dict',
             'value': "{'test':'test'}"}
        ]
        submit_tx_params = {'destination': str(self._score_address),
                            'method_name': 'set_wallet_owners_required',
                            'params': json.dumps(unsupported_type_params),
                            'description': 'change requirements 2 to 3'}

        result = transaction_call_error(super(), from_=self._operator,
                                        to_=self._score_address,
                                        method='submit_transaction',
                                        params=submit_tx_params,
                                        icon_service=self.icon_service
                                        )

        expected_revert_massage = "dict is not supported type (only dict_keys(['int', 'str', 'bool', 'Address', 'bytes']) are supported)"
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # failure case: invalid json format
        invalid_json_format_params = "{'test': }"

        submit_tx_params = {'destination': str(self._score_address),
                            'method_name': 'set_wallet_owners_required',
                            'params': invalid_json_format_params,
                            'description': 'change requirements 2 to 3'}

        result = transaction_call_error(super(), from_=self._operator,
                                        to_=self._score_address,
                                        method='submit_transaction',
                                        params=submit_tx_params,
                                        icon_service=self.icon_service
                                        )

        expected_revert_massage = "JSONDecodeError"
        actual_revert_massage = result['failure']['message']
        self.assertTrue(expected_revert_massage in actual_revert_massage)

    def test_submit_transaction_check_wallet_owner(self):
        # failure case: not included wallet owner
        change_requirement_params = [
            {'name': 'owners_required',
             'type': 'int',
             'value': '2'}
        ]
        submit_tx_params = {'destination': str(self._score_address),
                            'method_name': 'set_wallet_owners_required',
                            'params': json.dumps(change_requirement_params),
                            'description': 'change requirements 2 to 3'}

        result = transaction_call_error(super(), from_=self._attacker,
                                        to_=self._score_address,
                                        method='submit_transaction',
                                        params=submit_tx_params,
                                        icon_service=self.icon_service
                                        )

        expected_revert_massage = f'SenderNotMultisigOwnerError({self._attacker.get_address()})'
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

    def test_submit_transaction_check_result_format(self):
        self.change_req_to(2)

        actual_result = self.get_transaction(1)

        expected_result = {
            "uid": 1,
            "destination": f"{self._score_address}",
            "method_name": "set_wallet_owners_required",
            "params": '[{"name": "owners_required", "type": "int", "value": "2"}]',
            "amount": 0,
            "description": "change requirements to 2",
            "confirmations": [
                1
            ],
            "state": "EXECUTED"
        }

        self.assertEqual(expected_result, actual_result)

    def test_submit_transaction_check_transaction_list(self):
        # success case: submit 4 transaction and one transaction will be failed
        # transaction total count should be 3
        valid_params = [
            {'name': 'owners_required',
             'type': 'int',
             'value': '2'}
        ]
        invalid_params = [
            {'name': 'owners_required',
             'type': 'dict',
             'value': "{'test':'test'}"}
        ]

        # -------------------------
        valid_tx_params = {'destination': str(self._score_address),
                           'method_name': 'set_wallet_owners_required',
                           'params': json.dumps(valid_params),
                           'description': 'valid transaction1'}
        valid_tx1 = transaction_call_success(
            super(), from_=self._operator,
            to_=self._score_address,
            method='submit_transaction',
            params=valid_tx_params,
            icon_service=self.icon_service
        )

        # -------------------------
        valid_tx_params = {'destination': str(self._score_address),
                           'method_name': 'set_wallet_owners_required',
                           'params': json.dumps(valid_params),
                           'description': 'valid transaction2'}

        valid_tx2 = transaction_call_success(
            super(), from_=self._operator,
            to_=self._score_address,
            method='submit_transaction',
            params=valid_tx_params,
            icon_service=self.icon_service
        )

        # -------------------------
        invalid_tx_params = {
            'destination': str(self._score_address),
            'method_name': 'set_wallet_owners_required',
            'params': json.dumps(invalid_params),
            'description': 'invalid transaction'}

        invalid_tx = transaction_call_error(
            super(), from_=self._operator,
            to_=self._score_address,
            method='submit_transaction',
            params=invalid_tx_params
        )

        # -------------------------
        valid_tx_params = {'destination': str(self._score_address),
                           'method_name': 'set_wallet_owners_required',
                           'params': json.dumps(valid_params),
                           'description': 'valid transaction3'}
        valid_tx3 = transaction_call_success(
            super(), from_=self._operator,
            to_=self._score_address,
            method='submit_transaction',
            params=valid_tx_params,
            icon_service=self.icon_service
        )

        tx_results = [valid_tx1, valid_tx2, invalid_tx, valid_tx3]

        self.assertEqual(1, tx_results[0]['status'])
        self.assertEqual(1, tx_results[1]['status'])
        self.assertEqual(0, tx_results[2]['status'])
        self.assertEqual(1, tx_results[3]['status'])

        # check executed transaction count (should be 1, the first 1->2 req change)
        executed_transaction = self.get_executed_transactions_count()
        self.assertEqual(1, executed_transaction)

        # check executed transaction count (should be 2, the two valid transactions after the req change)
        waiting_transaction = self.get_waiting_transactions_count()
        self.assertEqual(2, waiting_transaction)
