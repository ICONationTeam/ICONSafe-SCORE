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


class TestIntegrateWalletMethod(MultiSigWalletTests):

    def setUp(self):
        super().setUp()

    def test_only_wallet_execute_method(self):
        # failure case: call method using normal owner
        # all external method which change the state of wallet(e.g. requirement) should be called by own wallet
        change_requirement_params = {"_required": "3"}
        change_requirement_tx = transaction_call_success(super(), from_=self._operator,
                                                         to_=self._score_address,
                                                         method="set_wallet_owners_required",
                                                         params=change_requirement_params,
                                                         icon_service=self.icon_service
                                                         )

        add_wallet_owner_params = {"_walletOwner": str(self._owner4)}
        add_wallet_owner_tx = transaction_call_success(super(), from_=self._operator,
                                                       to_=self._score_address,
                                                       method="addWalletOwner",
                                                       params=add_wallet_owner_params,
                                                       icon_service=self.icon_service
                                                       )

        replace_wallet_owner_params = {"_walletOwner": str(self._operator), "_newWalletOwner": str(self._owner4)}

        replace_wallet_owner_tx = transaction_call_success(super(), from_=self._operator,
                                                           to_=self._score_address,
                                                           method="replaceWalletOwner",
                                                           params=replace_wallet_owner_params,
                                                           icon_service=self.icon_service
                                                           )

        remove_wallet_owner_params = {"_walletOwner": str(self._operator)}
        remove_wallet_owner_tx = transaction_call_success(super(), from_=self._operator,
                                                          to_=self._score_address,
                                                          method="addWalletOwner",
                                                          params=remove_wallet_owner_params,
                                                          icon_service=self.icon_service
                                                          )

        prev_block, tx_results = self._make_and_req_block([change_requirement_tx,
                                                           add_wallet_owner_tx,
                                                           replace_wallet_owner_tx,
                                                           remove_wallet_owner_tx])

        for tx_result in tx_results:
            self.assertEqual(int(False), tx_result.status)

    def test_add_wallet_owner(self):
        # success case: add wallet owner4 successfully
        add_wallet_owner_params = [
            {"name": "_walletOwner",
             "type": "Address",
             "value": str(self._owner4)}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "addWalletOwner",
                            "_params": json.dumps(add_wallet_owner_params),
                            "_description": "add owner4 in wallet"}

        add_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                              to_=self._score_address,
                                                              method="submit_transaction",
                                                              params=submit_tx_params,
                                                              icon_service=self.icon_service
                                                              )
        prev_block, tx_results = self._make_and_req_block([add_wallet_owner_submit_tx])

        self.assertEqual(result['status'], int(True))

        # confirm transaction
        confirm_tx_params = {"transaction_uid": "0x00"}
        add_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._owner2,
                                                              to_=self._score_address,
                                                              method="confirm_transaction",
                                                              params=confirm_tx_params,
                                                              icon_service=self.icon_service
                                                              )
        prev_block, tx_results = self._make_and_req_block([add_wallet_owner_submit_tx])

        self.assertEqual(int(True), result['status'])

        # check wallet owners(owner4 should be added)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2), str(self._owner3), str(self._owner4)]
        self.assertEqual(response, expected_owners)

        # failure case: add already exist wallet owner
        add_wallet_owner_params = [
            {"name": "_walletOwner",
             "type": "Address",
             "value": str(self._operator)}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "addWalletOwner",
                            "_params": json.dumps(add_wallet_owner_params),
                            "_description": "add already exist wallet owner"}

        add_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                              to_=self._score_address,
                                                              method="submit_transaction",
                                                              params=submit_tx_params,
                                                              icon_service=self.icon_service
                                                              )
        prev_block, tx_results = self._make_and_req_block([add_wallet_owner_submit_tx])

        self.assertEqual(result['status'], int(True))

        # confirm transaction
        confirm_tx_params = {"transaction_uid": "0x01"}
        add_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._owner2,
                                                              to_=self._score_address,
                                                              method="confirm_transaction",
                                                              params=confirm_tx_params,
                                                              icon_service=self.icon_service
                                                              )
        prev_block, tx_results = self._make_and_req_block([add_wallet_owner_submit_tx])

        self.assertEqual(int(True), result['status'])

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[1].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # check wallet owners
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2), str(self._owner3), str(self._owner4)]
        self.assertEqual(response, expected_owners)

    def test_replace_wallet_owner(self):
        # success case: replace owner successfully(owner3 -> owner4)
        replace_wallet_owner_params = [
            {'name': '_walletOwner',
             'type': 'Address',
             'value': str(self._owner3)},
            {'name': '_newWalletOwner',
             'type': 'Address',
             'value': str(self._owner4)}
        ]
        replace_tx_params = {'destination': str(self._score_address),
                             'method_name': 'replaceWalletOwner',
                             'params': json.dumps(replace_wallet_owner_params),
                             'description': 'replace wallet owner'}

        replace_wallet_owner_tx = transaction_call_success(super(), from_=self._operator,
                                                           to_=self._score_address,
                                                           method="submit_transaction",
                                                           params=replace_tx_params,
                                                           icon_service=self.icon_service
                                                           )
        prev_block, tx_results = self._make_and_req_block([replace_wallet_owner_tx])

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

        self.assertEqual(True, result['status'])

        # check the wallet owner list(should be owner1, owner2, owner4)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2), str(self._owner4)]
        self.assertEqual(expected_owners, response)

        # failure case: try replace wallet owner who is not listed
        replace_wallet_owner_params = [
            {'name': '_walletOwner',
             'type': 'Address',
             'value': str(self._owner5)},
            {'name': '_newWalletOwner',
             'type': 'Address',
             'value': str(self._owner6)}
        ]
        replace_tx_params = {'destination': str(self._score_address),
                             'method_name': 'replaceWalletOwner',
                             'params': json.dumps(replace_wallet_owner_params),
                             'description': 'replace wallet owner'}

        replace_wallet_owner_tx = transaction_call_success(super(), from_=self._operator,
                                                           to_=self._score_address,
                                                           method="submit_transaction",
                                                           params=replace_tx_params,
                                                           icon_service=self.icon_service
                                                           )
        prev_block, tx_results = self._make_and_req_block([replace_wallet_owner_tx])

        self.assertEqual(int(True), result['status'])

        # confirm transaction
        valid_owner = self._owner2
        confirm_tx_params = {'transaction_uid': '0x01'}
        result = transaction_call_success(super(), from_=valid_owner,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        # check if the wallet owner list is not changed(should be owner1, owner2, owner4)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2), str(self._owner4)]
        self.assertEqual(expected_owners, response)

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[1].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # failure case: new wallet owner is already listed
        replace_wallet_owner_params = [
            {'name': '_walletOwner',
             'type': 'Address',
             'value': str(self._operator)},
            {'name': '_newWalletOwner',
             'type': 'Address',
             'value': str(self._owner4)}
        ]
        replace_tx_params = {'destination': str(self._score_address),
                             'method_name': 'replaceWalletOwner',
                             'params': json.dumps(replace_wallet_owner_params),
                             'description': 'replace wallet owner'}

        replace_wallet_owner_tx = transaction_call_success(super(), from_=self._operator,
                                                           to_=self._score_address,
                                                           method="submit_transaction",
                                                           params=replace_tx_params,
                                                           icon_service=self.icon_service
                                                           )
        prev_block, tx_results = self._make_and_req_block([replace_wallet_owner_tx])

        self.assertEqual(int(True), result['status'])

        # confirm transaction
        valid_owner = self._owner2
        confirm_tx_params = {'transaction_uid': '0x02'}
        result = transaction_call_success(super(), from_=valid_owner,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        # check if the wallet owner list is not changed(should be owner1, owner2, owner4)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2), str(self._owner4)]
        self.assertEqual(expected_owners, response)

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[1].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

    def test_remove_wallet_owner(self):
        # failure case: try to remove wallet owner who is not listed
        remove_wallet_owner_params = [
            {"name": "_walletOwner",
             "type": "Address",
             "value": str(self._owner4)}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "removeWalletOwner",
                            "_params": json.dumps(remove_wallet_owner_params),
                            "_description": "remove wallet owner4 in wallet"}

        remove_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                                 to_=self._score_address,
                                                                 method="submit_transaction",
                                                                 params=submit_tx_params,
                                                                 icon_service=self.icon_service
                                                                 )
        prev_block, tx_results = self._make_and_req_block([remove_wallet_owner_submit_tx])

        self.assertEqual(result['status'], int(True))

        # confirm transaction
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=self._owner2,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[1].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # check the wallet owner list(should be owner1, owner2, owner3)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2), str(self._owner3)]
        self.assertEqual(expected_owners, response)

        # success case: remove wallet owner successfully(remove owner3)
        remove_wallet_owner_params = [
            {"name": "_walletOwner",
             "type": "Address",
             "value": str(self._owner3)}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "removeWalletOwner",
                            "_params": json.dumps(remove_wallet_owner_params),
                            "_description": "remove wallet owner3 in wallet"}

        remove_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                                 to_=self._score_address,
                                                                 method="submit_transaction",
                                                                 params=submit_tx_params,
                                                                 icon_service=self.icon_service
                                                                 )
        prev_block, tx_results = self._make_and_req_block([remove_wallet_owner_submit_tx])

        self.assertEqual(True, result['status'])

        # confirm transaction
        confirm_tx_params = {'transaction_uid': '0x01'}
        result = transaction_call_success(super(), from_=self._owner2,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getTransactionsExecuted",
                "params": {"transaction_uid": "1"}
            }
        }
        response = self._query(query_request)
        self.assertEqual(True, response)

        # check execution success
        expected_execution_event_log = "Execution(int)"
        actual_execution_event_log = tx_results[0].event_logs[2].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # check the wallet owner list(should be owner1, owner2)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2)]
        self.assertEqual(expected_owners, response)

        # check the wallet owner3 is not wallet owner
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "checkIfWalletOwner",
                "params": {"_walletOwner": str(self._owner3)}
            }
        }
        expected_owners = False
        response = self._query(query_request)
        self.assertEqual(expected_owners, response)

        # failure case: try to remove wallet owner when owner's count is same as requirement
        # (should not be removed)
        remove_wallet_owner_params = [
            {"name": "_walletOwner",
             "type": "Address",
             "value": str(self._owner2)}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "removeWalletOwner",
                            "_params": json.dumps(remove_wallet_owner_params),
                            "_description": "remove wallet owner2 in wallet"}

        remove_wallet_owner_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                                 to_=self._score_address,
                                                                 method="submit_transaction",
                                                                 params=submit_tx_params,
                                                                 icon_service=self.icon_service
                                                                 )
        prev_block, tx_results = self._make_and_req_block([remove_wallet_owner_submit_tx])

        self.assertEqual(True, result['status'])

        # confirm transaction
        confirm_tx_params = {'transaction_uid': '0x02'}
        result = transaction_call_success(super(), from_=self._owner2,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getTransactionsExecuted",
                "params": {"transaction_uid": "2"}
            }
        }
        response = self._query(query_request)
        self.assertEqual(False, response)

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[1].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # check the wallet owner list(should be owner1, owner2)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getWalletOwners",
                "params": {"_offset": "0", "_count": "10"}
            }
        }
        response = self._query(query_request)
        expected_owners = [str(self._operator), str(self._owner2)]
        self.assertEqual(expected_owners, response)

    def test_change_requirement(self):
        # success case: change requirement 2 to 1
        change_requirement_params = [
            {"name": "_required",
             "type": "int",
             "value": 1}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "set_wallet_owners_required",
                            "_params": json.dumps(change_requirement_params),
                            "_description": "change requirement 2 to 1"}

        change_requirement_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                                to_=self._score_address,
                                                                method="submit_transaction",
                                                                params=submit_tx_params,
                                                                icon_service=self.icon_service
                                                                )
        prev_block, tx_results = self._make_and_req_block([change_requirement_submit_tx])

        self.assertEqual(result['status'], int(True))

        # confirm transaction
        confirm_tx_params = {'transaction_uid': '0x00'}
        result = transaction_call_success(super(), from_=self._owner2,
                                          to_=self._score_address,
                                          method='confirm_transaction',
                                          params=confirm_tx_params,
                                          icon_service=self.icon_service
                                          )
        prev_block, tx_results = self._make_and_req_block([confirm_tx])

        self.assertEqual(True, result['status'])

        # check the requirement(should be 1)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getRequirement",
                "params": {}
            }
        }
        expected_requirement = 1
        actual_requiremnt = self._query(query_request)
        self.assertEqual(expected_requirement, actual_requiremnt)

        # failure case: change requirement to 0
        change_requirement_params = [
            {"name": "_required",
             "type": "int",
             "value": 0}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "set_wallet_owners_required",
                            "_params": json.dumps(change_requirement_params),
                            "_description": "change requirement 1 to 0"}

        change_requirement_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                                to_=self._score_address,
                                                                method="submit_transaction",
                                                                params=submit_tx_params,
                                                                icon_service=self.icon_service
                                                                )
        prev_block, tx_results = self._make_and_req_block([change_requirement_submit_tx])

        self.assertEqual(result['status'], int(True))

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[2].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # check the requirement(should be 1)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getRequirement",
                "params": {}
            }
        }
        expected_requirement = 1
        actual_requiremnt = self._query(query_request)
        self.assertEqual(expected_requirement, actual_requiremnt)

        # failure case: try to set requirement more than owners
        change_requirement_params = [
            {"name": "_required",
             "type": "int",
             "value": 4}
        ]
        submit_tx_params = {"_destination": str(self._score_address),
                            "_method": "set_wallet_owners_required",
                            "_params": json.dumps(change_requirement_params),
                            "_description": "change requirement 1 to 4"}

        change_requirement_submit_tx = transaction_call_success(super(), from_=self._operator,
                                                                to_=self._score_address,
                                                                method="submit_transaction",
                                                                params=submit_tx_params,
                                                                icon_service=self.icon_service
                                                                )
        prev_block, tx_results = self._make_and_req_block([change_requirement_submit_tx])

        self.assertEqual(result['status'], int(True))

        # check execution failure
        expected_execution_event_log = "ExecutionFailure(int)"
        actual_execution_event_log = tx_results[0].event_logs[2].indexed[0]
        self.assertEqual(expected_execution_event_log, actual_execution_event_log)

        # check the requirement(should be 1)
        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": self._score_address,
            "dataType": "call",
            "data": {
                "method": "getRequirement",
                "params": {}
            }
        }
        expected_requirement = 1
        actual_requiremnt = self._query(query_request)
        self.assertEqual(expected_requirement, actual_requiremnt)
