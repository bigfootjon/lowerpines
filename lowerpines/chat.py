from lowerpines.endpoints.direct_message import Chat

from lowerpines import AbstractManager


class ChatManager(AbstractManager):
    def _all(self):
        return Chat.get_all(self.gmi)
