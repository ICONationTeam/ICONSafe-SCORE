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
from ..scorelib.auth import *
from ..scorelib.maintenance import *
from ..scorelib.exception import *
from ..scorelib.iterable_dict import *
from ..scorelib.linked_list import *
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
        return UIDLinkedListDB(f'{BalanceHistoryManager._NAME}_{str(token)}_balance_history', self.db)

    @property
    def _icx_balance_history(self) -> UIDLinkedListDB:
        return self._token_balance_history(ICX_TOKEN_ADDRESS)

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
    #  Internal methods
    # ================================================
    def update_icx_balance(self) -> None:
        current_balance = self.icx.get_balance(self.address)

        # Check for update in the last balance history item
        if len(self._icx_balance_history) > 0:
            last_balance_history_uid = self._icx_balance_history.head_value()
            last_balance_history = BalanceHistory(last_balance_history_uid, self.db)
            if last_balance_history._balance.get() == current_balance:
                # The last balance is the same, no need to update the balance history
                return

        balance_history_uid = BalanceHistoryFactory(self.db).create(ICX_TOKEN_ADDRESS, current_balance, self.tx.hash, self.now())
        self._icx_balance_history.prepend(balance_history_uid)
        self.BalanceHistoryCreated(balance_history_uid)

    # ================================================
    #  External methods
    # ================================================
    @external(readonly=True)
    @catch_exception
    def get_icx_balance_history(self, offset: int) -> dict:
        return [
            BalanceHistory(balance_history_uid, self.db).serialize()
            for balance_history_uid in self._icx_balance_history.select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_balance_history_item(self, balance_history_uid: int) -> dict:
        return BalanceHistory(balance_history_uid, self.db).serialize()
