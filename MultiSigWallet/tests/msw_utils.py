from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from MultiSigWallet.tests.utils import *

import json
import os

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class MultiSigWalletTests(IconIntegrateTestBase):

    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    IRC2_PROJECT = os.path.abspath(os.path.join(DIR_PATH, './irc2'))

    def setUp(self):
        super().setUp()

        self.icon_service = None

        # install SCORE
        self._operator = self._test1
        self._owner2 = self._wallet_array[0]
        self._owner3 = self._wallet_array[1]
        self._attacker = self._wallet_array[9]
        self._score_address = self._deploy_score(self.SCORE_PROJECT)['scoreAddress']

        for wallet in self._wallet_array:
            icx_transfer_call(
                super(), self._test1, wallet.get_address(), 100 * 10**18, self.icon_service)

        self._operator_icx_balance = get_icx_balance(super(), address=self._operator.get_address(), icon_service=self.icon_service)
        self._owner2_icx_balance = get_icx_balance(super(), address=self._owner2.get_address(), icon_service=self.icon_service)
        self._irc2_address = self._deploy_irc2(self.IRC2_PROJECT)['scoreAddress']
        self._irc2_address_2 = self._deploy_irc2(self.IRC2_PROJECT)['scoreAddress']

        irc2_transfer(super(), from_=self._operator, token=self._irc2_address, to_=self._owner2.get_address(), value=0x1000000, icon_service=self.icon_service)
        irc2_transfer(super(), from_=self._operator, token=self._irc2_address_2, to_=self._owner2.get_address(), value=0x1000000, icon_service=self.icon_service)
        self._operator_irc2_balance = get_irc2_balance(super(), address=self._operator.get_address(), token=self._irc2_address, icon_service=self.icon_service)
        self._owner2_irc2_balance = get_irc2_balance(super(), address=self._owner2.get_address(), token=self._irc2_address, icon_service=self.icon_service)

    def _deploy_score(self, project, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(project)) \
            .params({
                "owners": [{
                    "address": self._operator.get_address(),
                    "name": "operator"
                },
                    {
                    "address": self._owner2.get_address(),
                    "name": "user1"
                },
                    {
                    "address": self._owner3.get_address(),
                    "name": "user2"
                }],
                "owners_required": "0x1"
            }) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        result = self.process_transaction(
            signed_transaction, self.icon_service)

        self.assertTrue('status' in result)
        self.assertEqual(1, result['status'])
        self.assertTrue('scoreAddress' in result)

        return result

    def _deploy_irc2(self, project, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .params({
                "_initialSupply": 0x100000000000,
                "_decimals": 18,
                "_name": 'StandardToken',
                "_symbol": 'ST',
            }) \
            .from_(self._operator.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(project)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._operator)

        # process the transaction in local
        result = self.process_transaction(
            signed_transaction, self.icon_service)

        self.assertTrue('status' in result)
        self.assertEqual(1, result['status'])
        self.assertTrue('scoreAddress' in result)

        return result

    def get_executed_transactions_count(self) -> int:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="get_executed_transactions_count",
                icon_service=self.icon_service
            ), 0
        )

    def get_wallet_owners_required(self) -> int:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="get_wallet_owners_required",
                icon_service=self.icon_service
            ), 0
        )

    def get_waiting_transactions_count(self) -> int:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="get_waiting_transactions_count",
                icon_service=self.icon_service
            ), 0
        )

    def get_transaction(self, transaction_uid: int) -> dict:
        return icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_transaction",
            params={"transaction_uid": transaction_uid},
            icon_service=self.icon_service
        )

    def get_wallet_owner_uid(self, address: Address) -> int:
        return int(icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_wallet_owner_uid",
            params={"address": address},
            icon_service=self.icon_service
        ), 0)

    def _do_call(self, from_, method, params, success):
        call = transaction_call_success if success else transaction_call_error
        from_ = from_ if from_ else self._operator
        result = call(super(), from_=from_,
                      to_=self._score_address,
                      method=method,
                      params=params,
                      icon_service=self.icon_service)
        self.assertEqual(int(success), result['status'])
        return result

    def change_req_to(self, value: int, method_name: str = "set_wallet_owners_required", from_=None, success=True):
        valid_params = [
            {'name': 'owners_required',
             'type': 'int',
             'value': str(value)}
        ]

        params = {'destination': str(self._score_address),
                  'method_name': method_name,
                  'params': json.dumps(valid_params),
                  'description': 'change requirements to 2'}

        return self._do_call(from_, 'submit_transaction', params, success)

    def confirm_transaction(self, transaction_uid: int, from_=None, success=True):
        return self._do_call(
            from_,
            'confirm_transaction',
            {'transaction_uid': str(transaction_uid)},
            success
        )
