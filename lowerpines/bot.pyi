from typing import List

from lowerpines import AbstractManager
from lowerpines.endpoints.bot import Bot
from lowerpines.endpoints.group import Group


class BotManager(AbstractManager):
    def create(self, group: Group, name: str, callback_url: str=None, avatar_url: str=None) -> Bot: ...
    def _all(self) -> List[Bot]: ...
