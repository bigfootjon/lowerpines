from lowerpines.endpoints import Request


class Chat:
    created_at = None
    updated_at = None
    last_message = None
    messages_count = None
    other_user = None

    def __init__(self, gmi):
        self.gmi = gmi

    def get_all(self):
        return DirectMessageChatsRequest(self.gmi).result

    def get(self, other_user_id):
        return DirectMessageIndexRequest(self.gmi, other_user_id).result

    def post(self, source_guid, text, attachments=None):
        return DirectMessageCreateRequest(self.gmi, source_guid, self.other_user.user_id, text, attachments).result

    @classmethod
    def from_json(cls, gmi, json):
        chat = cls(gmi)

        chat.created_at = json['created_at']
        chat.updated_at = json['updated_at']
        chat.last_message = DirectMessage.from_json(gmi, json['last_message'])
        chat.messages_count = json['messages_count']
        chat.other_user = DirectMessageUser.from_json(gmi, json['other_user'])

        return chat

    def __str__(self):
        return "Chat with " + str(self.other_user)

    def __repr__(self):
        return "C:" + str(self.other_user)


class DirectMessage:
    attachments = None
    avatar_url = None
    conversation_id = None
    created_at = None
    favorited_by = None
    direct_message_id = None
    name = None
    recipient_id = None
    sender_id = None
    sender_type = None
    source_guid = None
    text = None
    user_id = None

    def __init__(self, gmi, source_guid=None, recipient_id=None, text=None, attachments=None):
        self.gmi = gmi
        self.source_guid = source_guid
        self.recipient_id = recipient_id
        self.text = text
        self.attachments = attachments

    def save(self):
        if self.direct_message_id is None:
            new_data = DirectMessageCreateRequest(self.gmi, self.source_guid, self.recipient_id, self.text,
                                                  self.attachments).result
            self._refresh_from_other(new_data)
        else:
            raise Exception("You cannot change a message that has already been sent")

    @classmethod
    def from_json(cls, gmi, json):
        dm = cls(gmi)

        dm.attachments = json['attachments']
        dm.avatar_url = json['avatar_url']
        dm.conversation_id = json['conversation_id']
        dm.created_at = json['created_at']
        dm.favorited_by = json['favorited_by']
        dm.direct_message_id = json['id']
        dm.name = json['name']
        dm.recipient_id = json['recipient_id']
        dm.sender_id = json['sender_id']
        dm.sender_type = json['sender_type']
        dm.source_guid = json['source_guid']
        dm.text = json['text']
        dm.user_id = json['user_id']

        return dm

    def _refresh_from_other(self, other):
        self.attachments = other.attachments
        self.avatar_url = other.avatar_url
        self.conversation_id = other.conversation_id
        self.created_at = other.created_at
        self.favorited_by = other.favorited_by
        self.direct_message_id = other.direct_message_id
        self.name = other.name
        self.recipient_id = other.recipient_id
        self.sender_id = other.sender_id
        self.sender_type = other.sender_type
        self.source_guid = other.source_guid
        self.text = other.text
        self.user_id = other.user_id

    def __str__(self):
        return self.text

    def __repr__(self):
        return "M:" + str(self)


class DirectMessageUser:
    avatar_url = None
    user_id = None
    name = None

    def __init__(self, gmi):
        self.gmi = gmi

    @classmethod
    def from_json(cls, gmi, json):
        user = cls(gmi)

        user.avatar_url = json['avatar_url']
        user.user_id = json['id']
        user.name = json['name']

        return user

    def __str__(self):
        return str(self.name)


class DirectMessageChatsRequest(Request):
    def __init__(self, gmi, page=None, per_page=None):
        self.page = page
        self.per_page = per_page
        super().__init__(gmi)

    def url(self):
        return self.base_url + '/chats'

    def args(self):
        arg_dict = {}
        if self.page is not None:
            arg_dict['page'] = self.page
        if self.per_page is not None:
            arg_dict['per_page'] = self.per_page
        return arg_dict

    def parse(self, response):
        chats = []
        for chat_json in response:
            chats.append(Chat.from_json(self.gmi, chat_json))
        return chats

    def mode(self):
        return "GET"


class DirectMessageIndexRequest(Request):
    def __init__(self, gmi, other_user_id, before_id=None, since_id=None):
        self.other_user_id = other_user_id
        if before_id and since_id:
            raise Exception('Cannot define both before_id and since_id!')
        self.before_id = before_id
        self.since_id = since_id
        super().__init__(gmi)

    def url(self):
        return self.base_url + '/direct_messages'

    def args(self):
        arg_dict = {
            'other_user_id': self.other_user_id
        }
        if self.before_id:
            arg_dict['before_id'] = self.before_id
        elif self.since_id:
            arg_dict['since_id'] = self.since_id
        return arg_dict

    def parse(self, response):
        dms = []
        for dm_json in response['direct_messages']:
            dms.append(DirectMessage.from_json(self.gmi, dm_json))
        return dms

    def mode(self):
        return "GET"


# This doesn't work. Don't know why
class DirectMessageCreateRequest(Request):
    def __init__(self, gmi, sender_id, recipient_id, text, attachments=None):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response):
        return DirectMessage.from_json(self.gmi, response['json'])

    def url(self):
        return self.base_url + '/direct_messages'

    def args(self):
        direct_message = {
            'text': self.text,
        }
        if self.attachments:
            direct_message['attachments'] = self.attachments
        return {
            # 'message': direct_message,
            'conversation_id': self.recipient_id + '+' + self.sender_id
        }

    def mode(self):
        return "POST"
