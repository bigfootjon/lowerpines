from lowerpines.endpoints import Request
from lowerpines.message import ComplexMessage


class Bot:
    bot_id = None
    group_id = None
    name = None
    avatar_url = None
    callback_url = None
    dm_notification = None

    def __init__(self, gmi, group_id=None, name=None, avatar_url=None, callback_url=None, dm_notification=None):
        self.gmi = gmi
        self.group_id = group_id
        self.name = name
        self.avatar_url = avatar_url
        self.callback_url = callback_url
        self.dm_notification = dm_notification

    @property
    def group(self):
        return self.gmi.groups.get(group_id=self.group_id)

    def save(self):
        if self.bot_id is None:
            new_data = BotCreateRequest(self.gmi, self.group_id, self.name, self.callback_url, self.avatar_url,
                                        self.dm_notification).result
            self._refresh_from_other(new_data)
        else:
            BotsUpdateRequest(self.gmi, self.bot_id, self.group_id, self.name, self.callback_url, self.avatar_url, self.dm_notification)

    def delete(self):
        if self.bot_id is None:
            raise Exception('Cannot destroy a bot that isn\'t saved!')
        else:
            BotDestroyRequest(self.gmi, self.bot_id)

    def _refresh_from_other(self, other):
        self.bot_id = other.bot_id
        self.group_id = other.group_id
        self.name = other.name
        self.avatar_url = other.avatar_url
        self.callback_url = other.callback_url
        self.dm_notification = other.dm_notification

    def refresh(self):
        if self.bot_id is None:
            raise Exception('This operation is not permitted')
        else:
            raise Exception('This is non trivial to implement')

    def post(self, text):
        if isinstance(text, ComplexMessage):
            BotPostRequest(self.gmi, self.bot_id, text.get_text(), text.get_attachments())
        else:
            BotPostRequest(self.gmi, self.bot_id, text)

    @staticmethod
    def get_all(gmi):
        return BotIndexRequest(gmi).result

    @staticmethod
    def get(gmi, bot_id):
        pass

    @classmethod
    def from_json(cls, gmi, json):
        bot = cls(gmi)
        bot.bot_id = json['bot_id']
        bot.group_id = json['group_id']
        bot.name = json['name']
        bot.avatar_url = json['avatar_url']
        bot.callback_url = json['callback_url']
        bot.dm_notification = json['dm_notification']

        return bot

    def __str__(self):
        return self.name + ':' + self.group_id


class BotCreateRequest(Request):
    def __init__(self, gmi, group_id, name, callback_url=None, avatar_url=None, dm_notification=None):
        self.name = name
        self.group_id = group_id
        self.dm_notification = dm_notification
        self.callback_url = callback_url
        self.avatar_url = avatar_url
        super().__init__(gmi)

    def parse(self, response):
        return Bot.from_json(self.gmi, response['bot'])

    def mode(self):
        return "POST"

    def url(self):
        return self.base_url + "/bots"

    def args(self):
        post_dict = {
            'bot': {
                'name': self.name,
                'group_id': self.group_id,
            }
        }
        if self.avatar_url is not None:
            post_dict['bot']['avatar_url'] = self.avatar_url
        if self.callback_url is not None:
            post_dict['bot']['callback_url'] = self.callback_url
        if self.dm_notification is not None:
            post_dict['bot']['dm_notification'] = self.dm_notification
        return post_dict


class BotPostRequest(Request):
    def __init__(self, gmi, bot_id, text, attachments=None):
        self.bot_id = bot_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response):
        return None

    def args(self):
        post_dict = {
            'bot_id': self.bot_id,
            'text': str(self.text),
        }
        if self.attachments is not None:
            post_dict['attachments'] = self.attachments
        return post_dict

    def mode(self):
        return "POST"

    def url(self):
        return self.base_url + '/bots/post'


class BotIndexRequest(Request):
    def parse(self, response):
        bots = []
        for bot_json in response:
            bots.append(Bot.from_json(self.gmi, bot_json))
        return bots

    def mode(self):
        return "GET"

    def url(self):
        return self.base_url + "/bots"


class BotDestroyRequest(Request):
    def __init__(self, gmi, bot_id):
        self.bot_id = bot_id
        super().__init__(gmi)

    def parse(self, response):
        return None

    def mode(self):
        return "POST"

    def url(self):
        return self.base_url + '/bots/destroy'

    def args(self):
        return {
            'bot_id': self.bot_id
        }


# --- Undocumented ---

class BotsUpdateRequest(Request):
    def __init__(self, gmi, bot_id, group_id=None, name=None, callback_url=None, avatar_url=None, dm_notification=None):
        self.group_id = group_id
        self.name = name
        self.avatar_url = avatar_url
        self.callback_url = callback_url
        self.dm_notification = dm_notification
        self.bot_id = bot_id
        super().__init__(gmi)

    def url(self):
        return self.base_url + '/bots/update'

    def mode(self):
        return "POST"

    def args(self):
        post_dict = {
            'bot': {
                'bot_id': self.bot_id,
            }
        }
        if self.group_id is not None:
            post_dict['bot']['group_id'] = self.group_id
        if self.name is not None:
            post_dict['bot']['name'] = self.name
        if self.avatar_url is not None:
            post_dict['bot']['avatar_url'] = self.avatar_url
        if self.callback_url is not None:
            post_dict['bot']['callback_url'] = self.callback_url
        if self.dm_notification is not None:
            post_dict['bot']['dm_notification'] = self.dm_notification
        if self.bot_id is not None:
            post_dict['bot']['bot_id'] = self.bot_id
        return post_dict

    def parse(self, response):
        pass
