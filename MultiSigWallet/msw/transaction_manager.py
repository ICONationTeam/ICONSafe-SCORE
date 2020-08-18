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
from ..scorelib.exception import *
from ..scorelib.linked_list import *
from .type_converter import *
from .wallet_owner import *
from .transaction import *


class TransactionParam(TypedDict):
    name: str
    type: str
    value: str


class TransactionManager:

    _NAME = 'TRANSACTION_MANAGER'

    # ================================================
    #  Fields
    # ================================================
    @property
    def _waiting_transactions(self) -> UIDLinkedListDB:
        return UIDLinkedListDB(f'{TransactionManager._NAME}_waiting_transactions', self.db)

    @property
    def _executed_transactions(self) -> UIDLinkedListDB:
        return UIDLinkedListDB(f'{TransactionManager._NAME}_executed_transactions', self.db)

    # ================================================
    #  Event Logs
    # ================================================
    @eventlog(indexed=1)
    def TransactionCreated(self, transaction_uid: int):
        pass

    @eventlog(indexed=2)
    def TransactionConfirmed(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @eventlog(indexed=2)
    def TransactionRevoked(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @eventlog(indexed=1)
    def TransactionExecutionSuccess(self, transaction_uid: int):
        pass

    @eventlog(indexed=1)
    def TransactionExecutionFailure(self, transaction_uid: int, error: str):
        pass

    # ================================================
    #  Checks
    # ================================================
    def _check_params_format_convertible(self, params: List[TransactionParam]):
        for param in params:
            ScoreTypeConverter.convert(param["type"], param["value"])

    # ================================================
    #  Internal methods
    # ================================================
    def _external_call(self, transaction: Transaction) -> None:
        method_name = transaction._method_name.get()

        if method_name == "":
            method_name = None

        params = {}
        if transaction._params.get() != "":
            for param in json_loads(transaction._params.get()):
                params[param["name"]] = ScoreTypeConverter.convert(param["type"], param["value"])

        destination = transaction._destination.get()
        amount = transaction._amount.get()

        if destination.is_contract and method_name != None:
            self.call(addr_to=destination,
                      func_name=method_name,
                      kw_dict=params,
                      amount=amount)
        else:
            self.icx.transfer(destination, amount)

    # ================================================
    #  External methods
    # ================================================
    @external
    @catch_exception
    @only_multisig_owner
    def submit_transaction(self,
                           destination: Address,
                           method_name: str = "",
                           params: str = "",
                           amount: int = 0,
                           description: str = "") -> None:

        # --- Checks ---
        if params:
            self._check_params_format_convertible(json_loads(params))

        if not destination.is_contract and (method_name or params):
            raise IconScoreException("Cannot set a method name or params to a EOA transfer transaction")

        # --- OK from here ---
        transaction_uid = TransactionFactory(self.db).create(
            destination,
            method_name,
            params,
            amount,
            description)

        self._waiting_transactions.append(transaction_uid)
        self.TransactionCreated(transaction_uid)

        self.confirm_transaction(transaction_uid)

    @external
    @catch_exception
    @only_multisig_owner
    def confirm_transaction(self, transaction_uid: int) -> None:
        transaction = Transaction(transaction_uid, self.db)
        wallet_owner_uid = self.get_wallet_owner_uid(self.msg.sender)

        # --- Checks ---
        transaction._state.check(TransactionState.WAITING)

        # --- OK from here ---
        transaction._confirmations.add(wallet_owner_uid)
        self.TransactionConfirmed(transaction_uid, wallet_owner_uid)

        if len(transaction._confirmations) >= self._wallet_owners_required.get():
            # Enough confirmations for the current transaction, execute it
            self._external_call(transaction)
            # Move the transaction from the waiting to the executed txs
            self._waiting_transactions.remove(transaction_uid)
            self._executed_transactions.append(transaction_uid)
            transaction._state.set(TransactionState.EXECUTED)
            self.TransactionExecutionSuccess(transaction._uid)

    @external
    @catch_exception
    @only_multisig_owner
    def revoke_transaction(self, transaction_uid: int) -> None:
        transaction = Transaction(transaction_uid, self.db)
        wallet_owner_uid = self.get_wallet_owner_uid(self.msg.sender)

        # --- Checks ---
        transaction._state.check(TransactionState.WAITING)
        transaction.check_has_confirmed(wallet_owner_uid)

        # --- OK from here ---
        transaction._confirmations.remove(wallet_owner_uid)
        self.TransactionRevoked(transaction_uid, wallet_owner_uid)

        if len(transaction._confirmations) == 0:
            # None wants this transaction anymore, cancel it
            transaction._state.set(TransactionState.CANCELLED)
            # Remove it from active transactions
            self._waiting_transactions.remove(transaction_uid)

    @external(readonly=True)
    @catch_exception
    def get_transaction(self, transaction_uid: int) -> dict:
        transaction = Transaction(transaction_uid, self.db)
        transaction._state.check_exists()
        return transaction.serialize()

    @external(readonly=True)
    @catch_exception
    def get_waiting_transactions(self, offset: int = 0) -> list:
        return [
            Transaction(transaction_uid, self.db).serialize()
            for transaction_uid in self._waiting_transactions.select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_executed_transactions(self, offset: int = 0) -> list:
        return [
            Transaction(transaction_uid, self.db).serialize()
            for transaction_uid in self._executed_transactions.select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_waiting_transactions_count(self) -> int:
        return len(self._waiting_transactions)

    @external(readonly=True)
    @catch_exception
    def get_executed_transactions_count(self) -> int:
        return len(self._executed_transactions)
