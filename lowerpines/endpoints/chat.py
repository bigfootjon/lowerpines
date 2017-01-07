from lowerpines.endpoints.object import AbstractObject, Field
from lowerpines.endpoints.request import Request
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message


class Chat(AbstractObject):
    created_at = Field()
    updated_at = Field()
    messages_count = Field()
    last_message_raw = Field(api_name='last_message', handler=dict)
    other_user_raw = Field(api_name='other_user', handler=dict)

    last_message = None
    other_user = None

    def __init__(self, gmi):
        self.gmi = gmi
        self.messages = ChatMessagesManager(self)

    @staticmethod
    def get_all(gmi):
        return DirectMessageChatsRequest(gmi).result

    def get(self, other_user_id):
        return DirectMessageIndexRequest(self.gmi, other_user_id).result

    def post(self, message):
        text, attachments = smart_split_complex_message(message)
        return DirectMessageCreateRequest(self.gmi, self.gmi.user.get().user_id, self.other_user.user_id, text,
                                          attachments).result

    def on_fields_loaded(self):
        self.last_message = DirectMessage.from_json(self.gmi, self.last_message_raw)
        self.other_user = DirectMessageUser.from_json(self.gmi, self.other_user_raw)

    def __str__(self):
        return "Chat with " + str(self.other_user)

    def __repr__(self):
        return "C:" + str(self.other_user)


class DirectMessage(AbstractObject):
    @staticmethod
    def get(gmi, *args):
        raise InvalidOperationException('This is non-trivial to implement')

    def refresh(self):
        raise InvalidOperationException('This is non-trivial to implement')

    field_map = {
        'attachments': 'attachments',
        'avatar_url': 'avatar_url',
        'conversation_id': 'conversation_id',
        'created_at': 'created_at',
        'favorited_by': 'favorited_by',
        'direct_message_id': 'id',
        'name': 'name',
        'recipient_id': 'recipient_id',
        'sender_id': 'sender_id',
        'sender_type': 'sender_type',
        'source_guid': 'source_guid',
        'text': 'text',
        'user_id': 'user_id',
    }

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
            raise InvalidOperationException("You cannot change a message that has already been sent")

    def __str__(self):
        return self.text

    def __repr__(self):
        return "M:" + str(self)


class DirectMessageUser(AbstractObject):
    def save(self):
        raise InvalidOperationException('This operation is not permitted')

    @staticmethod
    def get(gmi, *args):
        raise InvalidOperationException('This operation does not make sense')

    def refresh(self):
        raise InvalidOperationException('This operation is non-trivial to implement')

    field_map = {
        'avatar_url': 'avatar_url',
        'user_id': 'id',
        'name': 'name',
    }

    def __init__(self, gmi):
        self.gmi = gmi

    def __str__(self):
        return str(self.name)


class ChatMessagesManager:
    count = 0

    last_id = str()
    last_created_at = str()

    def __init__(self, chat):
        self.chat = chat

    def all(self):
        messages = self.recent()
        while len(messages) < self.count:
            messages.extend(self.before(messages[-1]))
        return messages

    def recent(self):
        return DirectMessageIndexRequest(self.chat.gmi, self.chat.other_user.user_id).result

    def before(self, message):
        return DirectMessageIndexRequest(self.chat.gmi, self.chat.other_user.user_id, before_id=message.message_id).result

    def since(self, message):
        return DirectMessageIndexRequest(self.chat.gmi, self.chat.group_id, since_id=message.message_id).result


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
            raise ValueError('Cannot define both before_id and since_id!')
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


class DirectMessageCreateRequest(Request):
    def __init__(self, gmi, sender_id, recipient_id, text, attachments=None):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response):
        # return DirectMessage.from_json(self.gmi, response['direct_message'])
        # TODO: Fix this
        pass

    def url(self):
        return self.base_url + '/direct_messages'

    def args(self):
        direct_message = {
            'text': self.text,
        }
        if self.attachments:
            direct_message['attachments'] = self.attachments
        return {
            'message': direct_message,
            'conversation_id': self.recipient_id + '+' + self.sender_id
        }

    def mode(self):
        return "POST"
