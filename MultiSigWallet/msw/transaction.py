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
from ..scorelib.set import *
from ..scorelib.state import *


class TransactionNotConfirmed(Exception):
    pass


class TransactionFactory(IdFactory):

    _NAME = 'TRANSACTION_FACTORY'

    def __init__(self, db: IconScoreDatabase):
        name = TransactionFactory._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db

    def create(self,
               destination: Address,
               method_name: str,
               params: str,
               amount: int,
               description: str) -> int:

        transaction_uid = self.get_uid()

        transaction = Transaction(transaction_uid, self._db)
        transaction._destination.set(destination)
        transaction._method_name.set(method_name)
        transaction._params.set(params)
        transaction._amount.set(amount)
        transaction._state.set(TransactionState.WAITING)
        transaction._description.set(description)

        return transaction_uid


class TransactionState:
    UNINITIALIZED = 0
    WAITING = 1
    EXECUTED = 2
    CANCELLED = 3
    FAILED = 4


class Transaction:

    _NAME = 'TRANSACTION'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{Transaction._NAME}_{uid}"
        self._destination = VarDB(f"{name}_destination", db, value_type=Address)
        self._method_name = VarDB(f"{name}_method_name", db, value_type=str)
        self._params = VarDB(f"{name}_params", db, value_type=str)
        self._amount = VarDB(f"{name}_amount", db, value_type=int)
        self._description = VarDB(f"{name}_description", db, value_type=str)
        self._confirmations = SetDB(f"{name}_confirmations", db, value_type=int)
        self._state = StateDB(f"{name}_state", db, value_type=TransactionState)
        self._uid = uid
        self._name = name
        self._db = db

    # ================================================
    #  Checks
    # ================================================
    def check_has_confirmed(self, wallet_owner_uid: int) -> None:
        if not wallet_owner_uid in self._confirmations:
            raise TransactionNotConfirmed(self._name, wallet_owner_uid)

    def serialize(self) -> dict:
        return {
            "uid": self._uid,
            "destination": str(self._destination.get()),
            "method_name": self._method_name.get(),
            "params": self._params.get(),
            "amount": self._amount.get(),
            "description": self._description.get(),
            "confirmations": list(self._confirmations),
            "state": self._state.get_name()
        }
