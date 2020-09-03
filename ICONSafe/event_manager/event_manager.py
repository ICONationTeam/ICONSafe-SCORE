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


class EventManager:

    _NAME = 'EVENT_MANAGER'

    # ================================================
    #  Fields
    # ================================================
    @property
    def _events(self) -> LinkedListDB:
        return LinkedListDB(f'{EventManager._NAME}_events', self.db, value_type=bytes)

    # ================================================
    #  Internal methods
    # ================================================
    def on_install_event_manager(self) -> None:
        pass

    def on_add_event(self) -> None:
        # A same tx may trigger multiple events
        if len(self._events) > 0 and self._events.head_value() == self.tx.hash:
            return

        if self.tx:  # deploy transaction may not have a txhash yet
            self._events.prepend(self.tx.hash)

    # ================================================
    #  External methods
    # ================================================
    @external(readonly=True)
    @catch_exception
    def get_events(self, offset: int = 0) -> list:
        return [
            {"uid": event_uid, "hash": event_hash}
            for event_uid, event_hash in self._events.select(offset)
        ]


def add_event(func):
    if not isfunction(func):
        raise NotAFunctionError

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):
        self.on_add_event()
        return func(self, *args, **kwargs)

    return __wrapper
