from lowerpines.manager import AbstractManager
from lowerpines.endpoints.bot import Bot


class BotManager(AbstractManager):
    def create(self, group, name, callback_url=None, avatar_url=None):
        bot = Bot(self.gmi, group.group_id, name, avatar_url, callback_url)
        bot.save()
        return bot

    def _all(self):
        return Bot.get_all(self.gmi)
