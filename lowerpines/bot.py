# pyre-strict

from typing import List, Optional, TYPE_CHECKING

from lowerpines.manager import AbstractManager
from lowerpines.endpoints.bot import Bot

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.endpoints.group import Group


class BotManager(AbstractManager[Bot]):
    def create(
        self,
        group: "Group",
        name: str,
        callback_url: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Bot:
        bot = Bot(self.gmi, group.group_id, name, avatar_url, callback_url)
        bot.save()
        return bot

    def _all(self) -> List[Bot]:
        return Bot.get_all(self.gmi)
