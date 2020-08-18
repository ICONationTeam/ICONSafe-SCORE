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
from MultiSigWallet.tests.utils import *

import json


class TestIntegrateSendToken(MultiSigWalletTests):

    def setUp(self):
        super().setUp()

    def send_token(self, value, to):
        return irc2_transfer(super(),
                             from_=self._operator,
                             token=str(self._irc2_address),
                             to_=to,
                             value=value,
                             icon_service=self.icon_service)

    def balance_token(self, address: Address):
        return get_irc2_balance(super(), str(address), str(self._irc2_address), icon_service=self.icon_service)

    def test_send_token(self):
        self.set_wallet_owners_required(2)

        # success case: send 500 token to user
        # deposit owner1's 1000 token to multisig wallet score
        self.send_token(1000, self._score_address)

        # check multisig wallet score's token amount(should be 1000)
        balance = self.balance_token(self._score_address)
        self.assertEqual(1000, balance)

        # check user's token amount(should be 0)
        balance = self.balance_token(self._user.get_address())
        self.assertEqual(0, balance)

        # make transaction which send 500 token to user
        result = self.msw_transfer_irc2(self._irc2_address, self._user.get_address(), 500)
        txuid = self.get_transaction_uid_created(result)

        # check confirmation count(should be 1)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 1)

        # confirm transaction
        self.confirm_transaction(txuid, from_=self._owner2)

        # check confirmation count(should be 2)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 2)

        # check user's token amount(should be 500)
        balance = self.balance_token(self._user.get_address())
        self.assertEqual(500, balance)

        # check multisig wallet's token amount(should be 500)
        balance = self.balance_token(self._score_address)
        self.assertEqual(500, balance)

    def test_send_token_revert(self):
        self.set_wallet_owners_required(2)

        # failure case: raise revert while sending 500 token to user.(500 token should not be sended)
        # deposit owner1's 1000 token to multisig wallet score
        self.send_token(1000, self._score_address)

        # check multisig wallet score's token amount(should be 1000)
        balance = self.balance_token(self._score_address)
        self.assertEqual(1000, balance)

        # check user's token amount(should be 0)
        balance = self.balance_token(self._user.get_address())
        self.assertEqual(0, balance)

        # make transaction which send 500 token to user (call revert_check method)
        result = self.msw_revert_check(self._irc2_address, self._user.get_address(), 500)
        txuid = self.get_transaction_uid_created(result)

        # confirm transaction
        self.confirm_transaction(txuid, from_=self._owner2, success=False)

        # check confirmation count(should be 1)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 1)

        # check transaction executed count(should be False)
        self.assertEqual("WAITING", transaction["state"])

        # check user's token amount(should be 0)
        balance = self.balance_token(self._user.get_address())
        self.assertEqual(0, balance)

        # check multisig wallet's token amount(should be 1000)
        balance = self.balance_token(self._score_address)
        self.assertEqual(1000, balance)
