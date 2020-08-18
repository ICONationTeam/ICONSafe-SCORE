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


class SenderNotMultisigOwnerError(Exception):
    pass


class WalletOwnerFactory(IdFactory):

    _NAME = 'WALLET_OWNER_FACTORY'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase):
        name = WalletOwnerFactory._NAME
        super().__init__(name, db)
        self._name = name
        self._db = db

    def create(self,
               address: Address,
               name: str) -> int:

        wallet_owner_uid = self.get_uid()

        owner = WalletOwner(wallet_owner_uid, self._db)

        owner._address.set(address)
        owner._name.set(name)

        return wallet_owner_uid


class WalletOwnerDescription(TypedDict):
    address: str
    name: str


class WalletOwner:

    _NAME = 'WALLET_OWNER'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{WalletOwner._NAME}_{uid}"
        self._address = VarDB(f"{name}_address", db, value_type=Address)
        self._name = VarDB(f"{name}_name", db, value_type=str)
        self._uid = uid
        self._db = db

    # ================================================
    #  Public methods
    # ================================================
    def serialize(self) -> dict:
        return {
            "uid": self._uid,
            "address": str(self._address.get()),
            "name": self._name.get()
        }


def only_multisig_owner(func):
    if not isfunction(func):
        raise NotAFunctionError

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):
        if not self.is_wallet_owner(self.msg.sender):
            raise SenderNotMultisigOwnerError(self.msg.sender)

        return func(self, *args, **kwargs)
    return __wrapper
