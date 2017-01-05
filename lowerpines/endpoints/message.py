from lowerpines.endpoints import Request
from lowerpines.endpoints.like import LikeCreateRequest, LikeDestroyRequest


class Message:
    message_id = None
    source_guid = None
    created_at = None
    user_id = None
    group_id = None
    name = None
    avatar_url = None
    text = None
    system = None
    favorited_by = None
    attachments = None
    sender_type = None
    sender_id = None
    complex_text = None

    def __init__(self, gmi, group_id=None, source_guid=None, text=None, attachments=list()):
        self.gmi = gmi
        self.group_id = group_id
        self.source_guid = source_guid
        self.text = text
        self.attachments = attachments

    def save(self):
        if self.message_id:
            raise Exception("You cannot change a message that has already been sent")
        else:
            new_data = MessagesCreateRequest(self.gmi, self.group_id, self.source_guid, self.text,
                                             self.attachments).result
            self._refresh_from_other(new_data)

    def refresh(self):
        if self.message_id:
            new_data = MessagesShowRequest(self.gmi, self.group_id, self.message_id).result
            self._refresh_from_other(new_data)
        else:
            raise Exception("Must have a message_id to pull data from the server")

    def _refresh_from_other(self, other):
        self.message_id = other.message_id
        self.source_guid = other.source_guid
        self.created_at = other.created_at
        self.user_id = other.user_id
        self.group_id = other.group_id
        self.name = other.name
        self.avatar_url = other.avatar_url
        self.text = other.text
        self.system = other.system
        self.favorited_by = other.favorited_by
        self.attachments = other.attachments
        self.sender_type = other.sender_type
        self.sender_id = other.sender_id

    @classmethod
    def from_json(cls, gmi, json):
        from lowerpines.message import ComplexMessage, RefAttach
        message = cls(gmi)
        message.message_id = json["id"]
        message.source_guid = json["source_guid"]
        message.created_at = json["created_at"]
        message.user_id = json["user_id"]
        message.group_id = json["group_id"]
        message.name = json["name"]
        message.avatar_url = json["avatar_url"]
        message.text = json["text"]
        if message.text is None:
            message.text = ""
        message.system = json["system"]
        message.favorited_by = json.get("favorited_by", [])
        message.complex_text = ComplexMessage('')
        message.attachments = json['attachments']
        doing_mentions = False
        for attachment in message.attachments:
            if attachment['type'] == 'mentions':
                doing_mentions = True
                prev_index = 0
                for i in range(len(message.text)):
                    for loci, user_id in zip(attachment['loci'], attachment['user_ids']):
                        if loci[0] == i:
                            message.complex_text += message.text[prev_index:loci[0]] + \
                                                    RefAttach(user_id, message.text[loci[0]:loci[0] + loci[1]])
                            prev_index = loci[0] + loci[1]
                message.complex_text = message.complex_text + message.text[prev_index:]
        if not doing_mentions:
            message.complex_text = ComplexMessage(message.text)
        message.sender_type = json['sender_type']
        message.sender_id = json['sender_id']
        return message

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.text

    @staticmethod
    def get(gmi, group_id, message_id):
        return MessagesShowRequest(gmi, group_id, message_id).result

    def like(self):
        LikeCreateRequest(self.gmi, self.group_id, self.message_id)

    def unlike(self):
        LikeDestroyRequest(self.gmi, self.group_id, self.message_id)


class MessagesIndexRequest(Request):
    def __init__(self, gmi, group_id, before_id=None, since_id=None, after_id=None, limit=20):
        self.group_id = group_id
        self.before_id = before_id
        self.since_id = since_id
        self.after_id = after_id
        self.limit = limit
        if limit > 100:
            raise Exception('Limit must be at or below 100')
        arg_count = 0
        if before_id is not None:
            arg_count += 1
        if since_id is not None:
            arg_count += 1
        if after_id is not None:
            arg_count += 1
        elif arg_count > 1:
            raise Exception('Only one of before_id, since_id or after_id can be defined')
        super().__init__(gmi)

    def mode(self):
        return "GET"

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/messages'

    def args(self):
        args_dict = {}
        if self.before_id is not None:
            args_dict['before_id'] = self.before_id
        if self.since_id is not None:
            args_dict['since_id'] = self.since_id
        if self.after_id is not None:
            args_dict['after_id'] = self.after_id
        if self.limit is not 20:
            args_dict['limit'] = self.limit
        return args_dict

    def parse(self, response):
        # count = int(response['count'])
        messages = []
        for message_json in response['messages']:
            messages.append(Message.from_json(self.gmi, message_json))
        return messages


class MessagesCreateRequest(Request):
    def __init__(self, gmi, group_id, source_guid, text, attachments=None):
        self.group_id = group_id
        self.source_guid = source_guid
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def mode(self):
        return "POST"

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/messages'

    def args(self):
        return {
            'message': {
                'source_guid': self.source_guid,
                'text': self.text,
                'attachments': self.attachments
            }
        }

    def parse(self, response):
        return Message.from_json(self.gmi, response['message'])


# --- Undocumented ---

class MessagesShowRequest(Request):
    def __init__(self, gmi, group_id, message_id):
        self.group_id = group_id
        self.message_id = message_id
        super().__init__(gmi)

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/messages/' + str(self.message_id)

    def mode(self):
        return "GET"

    def parse(self, response):
        return Message.from_json(self.gmi, response['message'])
