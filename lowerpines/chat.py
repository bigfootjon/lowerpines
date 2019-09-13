# pyre-strict

from typing import List

from lowerpines.endpoints.chat import Chat

from lowerpines.manager import AbstractManager


class ChatManager(AbstractManager[Chat]):
    def _all(self) -> List[Chat]:
        return Chat.get_all(self.gmi)
