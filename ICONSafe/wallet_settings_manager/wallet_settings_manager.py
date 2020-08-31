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


class WalletSettingsManager:

    _NAME = 'WALLET_SETTINGS_MANAGER'

    # ================================================
    #  Fields
    # ================================================
    @property
    def _safe_name(self) -> VarDB:
        return VarDB(f'{WalletSettingsManager._NAME}_safe_name', self.db, value_type=str)

    # ================================================
    #  External methods
    # ================================================
    @external(readonly=True)
    def get_safe_name(self) -> str:
        return self._safe_name.get()

    @external
    def set_safe_name(self, safe_name: str):
        self._safe_name.set(safe_name)
