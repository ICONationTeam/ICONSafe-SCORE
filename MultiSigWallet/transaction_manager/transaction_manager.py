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
from ..type_converter import *
from ..wallet_owner_manager import *

from .transaction import *
from .transaction_factory import *


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

    @property
    def _rejected_transactions(self) -> UIDLinkedListDB:
        return UIDLinkedListDB(f'{TransactionManager._NAME}_rejected_transactions', self.db)

    @property
    def _all_transactions(self) -> UIDLinkedListDB:
        return UIDLinkedListDB(f'{TransactionManager._NAME}_all_transactions', self.db)

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

    @eventlog(indexed=2)
    def TransactionRejected(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @eventlog(indexed=1)
    def TransactionCancelled(self, transaction_uid: int):
        pass

    @eventlog(indexed=1)
    def TransactionExecutionSuccess(self, transaction_uid: int):
        pass

    @eventlog(indexed=1)
    def TransactionRejectionSuccess(self, transaction_uid: int):
        pass

    @eventlog(indexed=1)
    def TransactionExecutionFailure(self, transaction_uid: int, error: str):
        pass

    # ================================================
    #  Checks
    # ================================================

    # ================================================
    #  Internal methods
    # ================================================
    def handle_incoming_transaction(self, token: Address, source: Address, amount: int) -> None:

        transaction_uid = TransactionFactory.create(
            self.db,
            TransactionType.INCOMING,
            self.tx.hash,
            self.now(),
            token, source, amount)

        self._all_transactions.append(transaction_uid)
        self.TransactionCreated(transaction_uid)

        self.update_balance_history_manager(transaction_uid)

    # ================================================
    #  Private methods
    # ================================================
    def _external_call(self, transaction: OutgoingTransaction) -> None:

        # Get the execution time, even if the subtx fails
        transaction._executed_timestamp.set(self.now())

        # Handle all sub transactions
        for sub_transaction_uid in transaction._sub_transactions:
            sub_transaction = SubOutgoingTransaction(sub_transaction_uid, self.db)

            method_name = sub_transaction._method_name.get() or None
            params = sub_transaction.convert_params()
            destination = sub_transaction._destination.get()
            amount = sub_transaction._amount.get()

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
    def submit_transaction(self, sub_transactions: str) -> None:

        transaction_uid = TransactionFactory.create(
            self.db,
            TransactionType.OUTGOING,
            self.tx.hash,
            self.now(),
            sub_transactions)

        self._waiting_transactions.append(transaction_uid)
        self._all_transactions.append(transaction_uid)
        self.TransactionCreated(transaction_uid)

    def _prepare_confirm_transaction(self, transaction_uid: int) -> Transaction:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.get_wallet_owner_uid(self.msg.sender)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)

        # --- OK from here ---
        transaction._confirmations.add(wallet_owner_uid)
        self.TransactionConfirmed(transaction_uid, wallet_owner_uid)

        if len(transaction._confirmations) >= self._wallet_owners_required.get():
            # Enough confirmations for the current transaction, execute it
            # Move the transaction from the waiting transactions
            self._waiting_transactions.remove(transaction_uid)
            self._executed_transactions.append(transaction_uid)
            transaction._executed_txhash.set(self.tx.hash)

        return transaction

    @external
    @catch_exception
    @only_multisig_owner
    def confirm_transaction(self, transaction_uid: int) -> None:
        transaction = self._prepare_confirm_transaction(transaction_uid)

        if len(transaction._confirmations) >= self._wallet_owners_required.get():
            # Enough confirmations for the current transaction, execute it
            try:
                self._external_call(transaction)
                # Call success
                self.update_balance_history_manager(transaction_uid)
                transaction._state.set(OutgoingTransactionState.EXECUTED)
                self.TransactionExecutionSuccess(transaction_uid)
            except BaseException as e:
                transaction._state.set(OutgoingTransactionState.FAILED)
                self.TransactionExecutionFailure(transaction_uid, repr(e))

    @external
    @catch_exception
    @only_multisig_owner
    def reject_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.get_wallet_owner_uid(self.msg.sender)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)

        # --- OK from here ---
        transaction._rejections.add(wallet_owner_uid)
        self.TransactionRejected(transaction_uid, wallet_owner_uid)

        if len(transaction._rejections) >= self._wallet_owners_required.get():
            # Enough confirmations for the current transaction, reject it

            # Move the transaction from the waiting transactions
            self._waiting_transactions.remove(transaction_uid)
            self._rejected_transactions.append(transaction_uid)

            # Call success
            transaction._state.set(OutgoingTransactionState.REJECTED)
            self.TransactionRejectionSuccess(transaction_uid)

    @external
    @catch_exception
    @only_multisig_owner
    def revoke_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.get_wallet_owner_uid(self.msg.sender)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)
        transaction.check_has_participated(wallet_owner_uid)

        # --- OK from here ---
        if transaction.has_confirmed(wallet_owner_uid):
            transaction._confirmations.remove(wallet_owner_uid)
        elif transaction.has_rejected(wallet_owner_uid):
            transaction._rejections.remove(wallet_owner_uid)

        self.TransactionRevoked(transaction_uid, wallet_owner_uid)

        if len(transaction._confirmations) == 0 and len(transaction._rejections) == 0:
            # None wants this transaction anymore, cancel it
            transaction._state.set(OutgoingTransactionState.CANCELLED)
            # Remove it from active transactions
            self._waiting_transactions.remove(transaction_uid)
            self._all_transactions.remove(transaction_uid)
            self.TransactionCancelled(transaction_uid)

    @external(readonly=True)
    @catch_exception
    def get_transaction(self, transaction_uid: int) -> dict:
        return self.serialize_transaction(transaction_uid)

    def serialize_transaction(self, transaction_uid: int) -> dict:
        transaction = Transaction(transaction_uid, self.db)
        transaction_type = transaction._type.get()

        if transaction_type == TransactionType.OUTGOING:
            return OutgoingTransaction(transaction_uid, self.db).serialize()
        elif transaction_type == TransactionType.INCOMING:
            return IncomingTransaction(transaction_uid, self.db).serialize()
        else:
            raise InvalidTransactionType(transaction._type.get())

    @external(readonly=True)
    @catch_exception
    def get_waiting_transactions(self, offset: int = 0) -> list:
        return [
            self.serialize_transaction(transaction_uid)
            for transaction_uid in self._waiting_transactions.select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_all_transactions(self, offset: int = 0) -> list:
        a = [
            self.serialize_transaction(transaction_uid)
            for transaction_uid in self._all_transactions.select(offset)
        ]
        Logger.warning(f'all = {a}')
        return a

    @external(readonly=True)
    @catch_exception
    def get_executed_transactions(self, offset: int = 0) -> list:
        return [
            self.serialize_transaction(transaction_uid)
            for transaction_uid in self._executed_transactions.select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_rejected_transactions(self, offset: int = 0) -> list:
        return [
            self.serialize_transaction(transaction_uid)
            for transaction_uid in self._rejected_transactions.select(offset)
        ]

    @external(readonly=True)
    @catch_exception
    def get_waiting_transactions_count(self) -> int:
        return len(self._waiting_transactions)

    @external(readonly=True)
    @catch_exception
    def get_all_transactions_count(self) -> int:
        return len(self._all_transactions)

    @external(readonly=True)
    @catch_exception
    def get_executed_transactions_count(self) -> int:
        return len(self._executed_transactions)

    @external(readonly=True)
    @catch_exception
    def get_rejected_transactions_count(self) -> int:
        return len(self._rejected_transactions)
