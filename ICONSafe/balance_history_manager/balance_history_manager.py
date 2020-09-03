# -*- coding: utf-8 -*-

# Copyright 2020 ICONation
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

from iconservice import *

from ..scorelib import *
from ..interfaces.irc2 import *
from ..wallet_owner_manager import *
from ..transaction_manager import *
from .consts import *
from .balance_history import *


class InvalidBalance(Exception):
    pass


class BalanceHistoryManager:

    _NAME = 'BALANCE_HISTORY_MANAGER'

    # ================================================
    #  Fields
    # ================================================
    def _token_balance_history(self, token: Address) -> UIDLinkedListDB:
        """ List of balance history items for any token """
        return UIDLinkedListDB(f'{BalanceHistoryManager._NAME}_{str(token)}_balance_history', self.db)

    @property
    def _tracked_balance_history(self) -> SetDB:
        """ List of tokens that are actively tracked for the balance history """
        return SetDB(f'{BalanceHistoryManager._NAME}_tokens_tracked', self.db, value_type=Address)

    # ================================================
    #  Event Logs
    # ================================================
    @eventlog(indexed=1)
    def BalanceHistoryCreated(self, balance_history_uid: int):
        pass

    # ================================================
    #  Checks
    # ================================================

    # ================================================
    #  Private methods
    # ================================================
    def _update_token_balance(self, transaction_uid: int, token: Address, current_balance: int) -> None:
        # Check for update in the last balance history item
        token_balance_history = self._token_balance_history(token)

        if len(token_balance_history) > 0:
            last_balance_history_uid = token_balance_history.head_value()
            last_balance_history = BalanceHistory(last_balance_history_uid, self.db)
            if last_balance_history._balance.get() == current_balance:
                # The last balance is the same, no need to update the balance history
                return

        balance_history_uid = BalanceHistoryFactory.create(self.db, transaction_uid, token, current_balance, self.now())
        token_balance_history.prepend(balance_history_uid)
        self.BalanceHistoryCreated(balance_history_uid)

    def _update_icx_balance(self, transaction_uid: int) -> None:
        current_balance = self.icx.get_balance(self.address)
        self._update_token_balance(transaction_uid, ICX_TOKEN_ADDRESS, current_balance)

    def _update_irc2_balance(self, transaction_uid: int, token: Address) -> None:
        irc2 = self.create_interface_score(token, IRC2Interface)
        current_balance = irc2.balanceOf(self.address)
        self._update_token_balance(transaction_uid, token, current_balance)

    # ================================================
    #  Internal methods
    # ================================================
    def on_install_balance_history_manager(self):
        # Track ICX balance by default
        self._tracked_balance_history.add(ICX_TOKEN_ADDRESS)
        self.update_balance_history_manager(SYSTEM_TRANSACTION_UID)

    def update_balance_history_manager(self, transaction_uid: int):
        for token in self._tracked_balance_history:
            if token == ICX_TOKEN_ADDRESS:
                self._update_icx_balance(transaction_uid)
            else:
                self._update_irc2_balance(transaction_uid, token)

    # ================================================
    #  External methods
    # ================================================
    @external(readonly=True)
    @catch_exception
    def get_token_balance_history(self, token: Address, offset: int = 0) -> list:
        return [
            self.get_balance_history(balance_history_uid)
            for balance_history_uid in self._token_balance_history(token).select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_balance_history(self, balance_history_uid: int) -> dict:
        return BalanceHistory(balance_history_uid, self.db).serialize()

    @external(readonly=True)
    @catch_exception
    def get_balance_trackers(self, offset: int = 0) -> list:
        return self._tracked_balance_history.select(offset)

    @external
    @catch_exception
    @only_multisig_owner
    def add_balance_tracker(self, token: Address) -> None:
        self._tracked_balance_history.add(token)
        self.update_balance_history_manager(SYSTEM_TRANSACTION_UID)

    @external
    @catch_exception
    @only_multisig_owner
    def remove_balance_tracker(self, token: Address) -> None:
        self._tracked_balance_history.remove(token)
        self.update_balance_history_manager(SYSTEM_TRANSACTION_UID)
