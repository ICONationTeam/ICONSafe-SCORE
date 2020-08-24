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

from .wallet_owner import *
from .wallet_owner_factory import *


class InvalidWalletRequirements(Exception):
    pass


class WalletOwnerDoesntExist(Exception):
    pass


class WalletAddressAlreadyExist(Exception):
    pass


class WalletOwnerDescription(TypedDict):
    address: str
    name: str


class WalletOwnersManager:

    _NAME = 'WALLET_OWNERS_MANAGER'
    _MAX_WALLET_OWNER_COUNT = 100

    # ================================================
    #  Fields
    # ================================================
    @property
    def _wallet_owners(self) -> UIDLinkedListDB:
        return UIDLinkedListDB(f'{WalletOwnersManager._NAME}_wallet_owners', self.db)

    @property
    def _address_to_uid_map(self) -> DictDB:
        return DictDB(f'{WalletOwnersManager._NAME}_ADDRESS_TO_UID_MAP', self.db, value_type=int)

    @property
    def _wallet_owners_required(self) -> VarDB:
        return VarDB(f'{WalletOwnersManager._NAME}_wallet_owners_required', self.db, value_type=int)

    # ================================================
    #  Event Logs
    # ================================================
    @eventlog(indexed=1)
    def WalletOwnerAddition(self, wallet_owner_uid: int):
        pass

    @eventlog(indexed=1)
    def WalletOwnerRemoval(self, wallet_owner_uid: int):
        pass

    # ================================================
    #  Checks
    # ================================================
    @staticmethod
    def _check_requirements(wallet_owner_count: int, owners_required: int):
        if (wallet_owner_count > WalletOwnersManager._MAX_WALLET_OWNER_COUNT or
                owners_required > wallet_owner_count or
                owners_required <= 0 or
                wallet_owner_count == 0):
            raise InvalidWalletRequirements(wallet_owner_count, owners_required)

    def _check_address_doesnt_exist(self, address: Address):
        if self.is_wallet_owner(address):
            raise WalletAddressAlreadyExist(address)

    def _check_exists(self, address: Address) -> None:
        if self._address_to_uid_map[str(address)] == 0:
            raise WalletOwnerDoesntExist(WalletOwnersManager._NAME, str(address))

    # ================================================
    #  Private methods
    # ================================================
    def _add_wallet_owner(self, address: Address, wallet_owner_uid: int) -> int:
        self._wallet_owners.append(wallet_owner_uid)
        self._address_to_uid_map[str(address)] = wallet_owner_uid
        self.WalletOwnerAddition(wallet_owner_uid)

    def _remove_wallet_owner(self, wallet_owner_uid: int) -> int:
        owner = WalletOwner(wallet_owner_uid, self.db)
        self._wallet_owners.remove(wallet_owner_uid)
        self._address_to_uid_map.remove(str(owner._address.get()))
        self.WalletOwnerRemoval(wallet_owner_uid)

    # ================================================
    #  Internal methods
    # ================================================
    def on_install_wallet_owner_manager(self, owners: List[WalletOwnerDescription], owners_required: int):
        # --- Checks ---
        WalletOwnersManager._check_requirements(len(owners), owners_required)
        self._wallet_owners_required.set(owners_required)

        for owner in owners:
            address = Address.from_string(owner['address'])
            self._check_address_doesnt_exist(address)

        # --- OK from here ---
        for owner in owners:
            address, name = Address.from_string(owner['address']), owner['name']
            wallet_owner_uid = WalletOwnerFactory.create(self.db, address, name)
            self._add_wallet_owner(address, wallet_owner_uid)

    # ================================================
    #  Only Wallet External methods
    # ================================================
    @catch_exception
    @only_wallet
    @external
    def add_wallet_owner(self, address: Address, name: str) -> None:
        # --- Checks ---
        WalletOwnersManager._check_requirements(len(self._wallet_owners) + 1, self._wallet_owners_required.get())
        self._check_address_doesnt_exist(address)
        # --- OK from here ---
        wallet_owner_uid = WalletOwnerFactory.create(self.db, address, name)
        self._add_wallet_owner(address, wallet_owner_uid)

    @catch_exception
    @only_wallet
    @external
    def remove_wallet_owner(self, wallet_owner_uid: int) -> None:
        # --- Checks ---
        WalletOwnersManager._check_requirements(len(self._wallet_owners) - 1, self._wallet_owners_required.get())

        # --- OK from here ---
        self._remove_wallet_owner(wallet_owner_uid)

    @catch_exception
    @only_wallet
    @external
    def replace_wallet_owner(self, old_wallet_owner_uid: int, new_address: Address, new_name: str) -> None:
        # --- Checks ---
        WalletOwnersManager._check_requirements(len(self._wallet_owners), self._wallet_owners_required.get())
        self._check_address_doesnt_exist(new_address)
        # --- OK from here ---
        new_wallet_owner_uid = WalletOwnerFactory.create(self.db, new_address, new_name)
        self._remove_wallet_owner(old_wallet_owner_uid)
        self._add_wallet_owner(new_address, new_wallet_owner_uid)

    @catch_exception
    @only_wallet
    @external
    def set_wallet_owners_required(self, owners_required: int) -> None:
        # --- Checks ---
        WalletOwnersManager._check_requirements(len(self._wallet_owners), owners_required)
        # --- OK from here ---
        self._wallet_owners_required.set(owners_required)

    # ================================================
    #  External methods
    # ================================================
    @catch_exception
    @external(readonly=True)
    def get_wallet_owners(self, offset: int = 0) -> list:
        return [
            self.get_wallet_owner(wallet_owner_uid)
            for wallet_owner_uid in self._wallet_owners.select(offset)
        ]

    @catch_exception
    @external(readonly=True)
    def get_wallet_owner(self, wallet_owner_uid: int) -> dict:
        return WalletOwner(wallet_owner_uid, self.db).serialize()

    @catch_exception
    @external(readonly=True)
    def get_wallet_owner_uid(self, address: Address) -> int:
        self._check_exists(address)
        return self._address_to_uid_map[str(address)]

    @catch_exception
    @external(readonly=True)
    def get_wallet_owners_count(self) -> int:
        return len(self._wallet_owners)

    @catch_exception
    @external(readonly=True)
    def is_wallet_owner(self, address: Address) -> bool:
        return self._address_to_uid_map[str(address)] != 0

    @catch_exception
    @external(readonly=True)
    def get_wallet_owners_required(self) -> int:
        return self._wallet_owners_required.get()
