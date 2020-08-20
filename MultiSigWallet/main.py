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
from .scorelib.maintenance import *
from .scorelib.version import *
from .scorelib.exception import *
from .scorelib.auth import *
from .msw.wallet_owner import *
from .msw.wallet_owner_manager import *
from .msw.transaction import *
from .msw.transaction_manager import *
from .consts import *


class MultiSigWallet(IconScoreBase,
                     IconScoreMaintenance,
                     IconScoreVersion,
                     IconScoreExceptionHandler,
                     WalletOwnersManager,
                     TransactionManager):

    _NAME = 'MultiSigWallet'

    # ================================================
    #  Event Logs
    # ================================================

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self, owners: List[WalletOwnerDescription], owners_required: int) -> None:
        super().on_install()
        self._version_update(VERSION)

        # --- Checks ---
        self._check_requirements(len(owners), owners_required)
        self._wallet_owners_required.set(owners_required)

        for owner in owners:
            address = Address.from_string(owner['address'])
            self._check_address_doesnt_exist(address)

        # --- OK from here ---
        for owner in owners:
            address, name = Address.from_string(owner['address']), owner['name']
            wallet_owner_uid = WalletOwnerFactory(self.db).create(address, name)
            self._add_wallet_owner(address, wallet_owner_uid)

    def on_update(self, owners: List[WalletOwnerDescription], owners_required: int) -> None:
        super().on_update()

        # if self._is_less_than_target_version('0.1.0'):
        #     self._migrate_v0_1_0()

        self._version_update(VERSION)

    # ================================================
    #  External methods
    # ================================================
    @catch_exception
    @check_maintenance
    @payable
    def fallback(self):
        pass

    @catch_exception
    @check_maintenance
    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        pass

    @external(readonly=True)
    def name(self) -> str:
        return MultiSigWallet._NAME
