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

from ..scorelib.state import *


class TransactionType:
    UNINITIALIZED = 0
    OUTGOING = 1
    INCOMING = 2


class Transaction:

    _NAME = 'TRANSACTION'

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{Transaction._NAME}_{uid}"
        self._type = StateDB(f"{name}_type", db, value_type=TransactionType)
        self._timestamp = VarDB(f"{name}_timestamp", db, value_type=int)
        self._txhash = VarDB(f"{name}_txhash", db, value_type=bytes)
        self._uid = uid
        self._name = name
        self._db = db

    def build(self, txtype: int, timestamp: int, txhash: bytes) -> None:
        self._type.set(txtype)
        self._timestamp.set(timestamp)
        self._txhash.set(txhash)

    # ================================================
    #  Internal methods
    # ================================================
    def serialize(self) -> dict:
        return {
            "uid": self._uid,
            "type": self._type.get_name(),
            "txhash": f"0x{bytes.hex(self._txhash.get())}" if self._txhash.get() else "None",
            "timestamp": self._timestamp.get()
        }
