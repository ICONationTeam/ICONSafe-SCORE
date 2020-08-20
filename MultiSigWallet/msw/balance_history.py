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
from ..scorelib.id_factory import *


class BalanceHistoryFactory(IdFactory):

    _NAME = 'BALANCE_HISTORY_FACTORY'

    def __init__(self, db: IconScoreDatabase):
        name = BalanceHistoryFactory._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db

    def create(self,
               token: Address,
               balance: int,
               txhash: bytes,
               timestamp: int) -> int:

        balance_history_uid = self.get_uid()

        balance_history = BalanceHistory(balance_history_uid, self._db)
        balance_history._token.set(token)
        balance_history._balance.set(balance)
        balance_history._txhash.set(txhash)
        balance_history._timestamp.set(timestamp)

        return balance_history_uid


class BalanceHistory:

    _NAME = 'BALANCE_HISTORY'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{BalanceHistory._NAME}_{uid}"
        self._token = VarDB(f"{name}_token", db, value_type=Address)
        self._balance = VarDB(f"{name}_balance", db, value_type=int)
        self._txhash = VarDB(f"{name}_txhash", db, value_type=bytes)
        self._timestamp = VarDB(f"{name}_timestamp", db, value_type=int)
        self._uid = uid
        self._name = name
        self._db = db

    # ================================================
    #  Checks
    # ================================================
    def serialize(self) -> dict:
        return {
            "uid": self._uid,
            "token": str(self._token.get()),
            "balance": self._balance.get(),
            "txhash": bytes.hex(self._txhash.get()) if self._txhash.get() else "None",
            "timestamp": self._timestamp.get()
        }
