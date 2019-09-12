# pyre-strict
from typing import List, TYPE_CHECKING

from lowerpines.endpoints.chat import Chat

from lowerpines.manager import AbstractManager

if TYPE_CHECKING:
    from lowerpines.endpoints.chat import DirectMessage


class ChatManager(AbstractManager['DirectMessage']):
    def _all(self) -> List['DirectMessage']:
        return Chat.get_all(self.gmi)
