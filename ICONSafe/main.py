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

from .scorelib import *
from .consts import *

from .wallet_owner_manager import *
from .transaction_manager import *
from .balance_history_manager import *
from .wallet_settings_manager import *


class ICONSafe(IconScoreBase,
               IconScoreMaintenance,
               IconScoreVersion,
               IconScoreExceptionHandler,
               WalletOwnersManager,
               TransactionManager,
               BalanceHistoryManager,
               WalletSettingsManager):

    _NAME = 'ICONSafe'

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
        self.on_install_version_manager(VERSION)
        self.on_install_wallet_settings_manager(DEFAULT_NAME)
        self.on_install_maintenance_manager(IconScoreMaintenanceStatus.DISABLED)
        self.on_install_balance_history_manager()
        self.on_install_wallet_owner_manager(owners, owners_required)

    def on_update(self, owners: List[WalletOwnerDescription], owners_required: int) -> None:
        super().on_update()

        # if self._is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.on_update_version_manager(VERSION)

    # ================================================
    #  External methods
    # ================================================
    @external(readonly=True)
    def name(self) -> str:
        return ICONSafe._NAME

    @catch_exception
    @check_maintenance
    @payable
    def fallback(self):
        self.handle_incoming_transaction(ICX_TOKEN_ADDRESS, self.msg.sender, self.msg.value)

    @catch_exception
    @check_maintenance
    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        self.handle_incoming_transaction(self.msg.sender, _from, _value)
