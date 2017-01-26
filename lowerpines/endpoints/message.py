from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.endpoints.like import LikeCreateRequest, LikeDestroyRequest
from lowerpines.exceptions import InvalidOperationException


class Message(AbstractObject, RetrievableObject):
    message_id = Field(api_name='id')
    source_guid = Field()
    created_at = Field()
    user_id = Field()
    group_id = Field()
    name = Field()
    avatar_url = Field()
    text = Field()
    system = Field()
    favorited_by = Field(handler=None)
    attachments = Field(handler=None)
    sender_type = Field()
    sender_id = Field()

    def __init__(self, gmi, group_id=None, source_guid=None, text=None, attachments=list()):
        self.gmi = gmi
        self.group_id = group_id
        self.source_guid = source_guid
        self.text = text
        self.attachments = attachments
        self.message_id = None

    def save(self):
        if self.message_id:
            raise InvalidOperationException("You cannot change a message that has already been sent")
        else:
            new_data = MessagesCreateRequest(self.gmi, self.group_id, self.source_guid, self.text,
                                             self.attachments).result
            self._refresh_from_other(new_data)

    def refresh(self):
        if self.message_id:
            new_data = MessagesShowRequest(self.gmi, self.group_id, self.message_id).result
            self._refresh_from_other(new_data)
        else:
            raise InvalidOperationException("Must have a message_id to pull data from the server")

    def on_fields_loaded(self):
        if self.text is None:
            self.text = ""
        from lowerpines.message import ComplexMessage, RefAttach
        self.complex_text = ComplexMessage('')
        doing_mentions = False
        for attachment in self.attachments:
            if attachment['type'] == 'mentions':
                doing_mentions = True
                prev_index = 0
                for i in range(len(self.text)):
                    for loci, user_id in zip(attachment['loci'], attachment['user_ids']):
                        if loci[0] == i:
                            self.complex_text += self.text[prev_index:loci[0]] + \
                                                    RefAttach(user_id, self.text[loci[0]:loci[0] + loci[1]])
                            prev_index = loci[0] + loci[1]
                self.complex_text = self.complex_text + self.text[prev_index:]
        if not doing_mentions:
            self.complex_text = ComplexMessage(self.text)

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
            raise ValueError('Limit must be at or below 100')
        arg_count = 0
        if before_id is not None:
            arg_count += 1
        if since_id is not None:
            arg_count += 1
        if after_id is not None:
            arg_count += 1
        elif arg_count > 1:
            raise ValueError('Only one of before_id, since_id or after_id can be defined')
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
