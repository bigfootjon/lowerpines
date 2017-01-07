from datetime import datetime

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.endpoints.member import MembersAddRequest, MembersRemoveRequest, Member
from lowerpines.endpoints.message import Message
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message


class Group(AbstractObject, RetrievableObject):
    group_id = Field(api_name='id')
    name = Field()
    type = Field()
    description = Field()
    image_url = Field()
    creator_user_id = Field()
    created_at = Field()
    updated_at = Field()
    share_url = Field()
    members_raw = Field(api_name='members', handler=None)
    messages_count_raw = Field(api_name='messages.count', handler=None)
    messages_last_message_id_raw = Field(api_name='messages.last_message_id', handler=None)
    messages_last_message_created_at_raw = Field(api_name='messages.last_message_created_at', handler=None)

    def __init__(self, gmi, name=None, description=None, image_url=None):
        super().__init__()
        self.gmi = gmi
        self.messages = GroupMessagesManager(self)
        self.name = name
        self.description = description
        self.image_url = image_url
        self.members = []

    @property
    def bots(self):
        return self.gmi.bots.filter(group_id=self.group_id)

    def on_fields_loaded(self):
        self.members = []
        for member_json in self.members_raw:
            self.members.append(Member.from_json(self.gmi, member_json, self.group_id))
        self.messages.count = self.messages_count_raw
        self.messages.last_id = self.messages_last_message_id_raw
        self.messages.last_created_at = self.messages_last_message_created_at_raw

    def save(self):
        if self.group_id is None:
            new_data = GroupsCreateRequest(self.gmi, self.name, self.description, self.image_url).result
        else:
            new_data = GroupsUpdateRequest(self.gmi, self.group_id, self.name, self.description, self.image_url).result

        self._refresh_from_other(new_data)

    def delete(self):
        if self.group_id is None:
            raise InvalidOperationException('Cannot destroy a group that isn\'t saved!')
        else:
            GroupsDestroyRequest(self.gmi, self.group_id)

    def refresh(self):
        if self.group_id is None:
            raise InvalidOperationException('Must have an id to perform this operation')
        else:
            new_data = GroupsShowRequest(self.gmi, group_id=self.group_id).result
            self._refresh_from_other(new_data)

    def member_add(self, name, user_id):
        MembersAddRequest(self.gmi, self.group_id, name, user_id=user_id)

    def member_rm(self, member_id):
        MembersRemoveRequest(self.gmi, self.group_id, member_id)

    def post(self, message):
        text, attachments = smart_split_complex_message(message)
        obj = Message(self.gmi, self.group_id, str(datetime.now()), text, attachments)
        obj.save()
        return obj

    @staticmethod
    def get(gmi, group_id):
        return GroupsShowRequest(gmi, group_id).result

    @staticmethod
    def get_all(gmi):
        return GroupsIndexRequest(gmi, per_page=100).result

    @staticmethod
    def get_former(gmi):
        return GroupsFormerRequest(gmi).result

    @staticmethod
    def join(gmi, group_id, share_token):
        return GroupsJoinRequest(gmi, group_id, share_token).result

    @staticmethod
    def rejoin(gmi, group_id):
        return GroupsRejoinRequest(gmi, group_id).result

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class GroupMessagesManager:
    count = 0

    last_id = str()
    last_created_at = str()

    def __init__(self, group):
        self.group = group

    def all(self):
        messages = self.recent()
        while len(messages) < self.count:
            messages.extend(self.before(messages[-1]))
        return messages

    def recent(self, count=100):
        from lowerpines.endpoints.message import MessagesIndexRequest
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count).result

    def before(self, message, count=100):
        from lowerpines.endpoints.message import MessagesIndexRequest
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count,
                                    before_id=message.message_id).result

    def since(self, message, count=100):
        from lowerpines.endpoints.message import MessagesIndexRequest
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count,
                                    since_id=message.message_id).result

    def after(self, message, count=100):
        from lowerpines.endpoints.message import MessagesIndexRequest
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count,
                                    after_id=message.message_id).result


class GroupsIndexRequest(Request):
    def __init__(self, gmi, page=1, per_page=10):
        self.page = page
        self.per_page = per_page
        super().__init__(gmi)

    def url(self):
        return self.base_url + "/groups"

    def args(self):
        return {
            'page': self.page,
            'per_page': self.per_page
        }

    def mode(self):
        return "GET"

    def parse(self, response):
        groups = []
        for group_json in response:
            groups.append(Group.from_json(self.gmi, group_json))
        return groups


class GroupsFormerRequest(Request):
    def url(self):
        return self.base_url + "/groups/former"

    def args(self):
        return {}

    def mode(self):
        return "GET"

    def parse(self, response):
        groups = []
        for group_json in response:
            groups.append(Group.from_json(self.gmi, group_json))
        return groups


class GroupsShowRequest(Request):
    def __init__(self, gmi, group_id):
        self.group_id = group_id
        super().__init__(gmi)

    def url(self):
        return self.base_url + "/groups/" + str(self.group_id)

    def args(self):
        return {}

    def mode(self):
        return "GET"

    def parse(self, response):
        return Group.from_json(self.gmi, response)


class GroupsCreateRequest(Request):
    def parse(self, response):
        return Group.from_json(self.gmi, response)

    def __init__(self, gmi, name, description=None, image_url=None, share=None):
        self.name = name
        self.description = description
        self.image_url = image_url
        self.share = share
        super().__init__(gmi)

    def url(self):
        return self.base_url + "/groups"

    def mode(self):
        return "POST"

    def args(self):
        post_args = {
            'name': self.name
        }
        if self.description is not None:
            post_args['description'] = self.description
        if self.image_url is not None:
            post_args['image_url'] = self.image_url
        if self.share is not None:
            post_args['share'] = self.share
        return post_args


class GroupsUpdateRequest(Request):
    def __init__(self, gmi, group_id, name=None, description=None, image_url=None, office_mode=None, share=None):
        self.group_id = group_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.office_mode = office_mode
        self.share = share
        super().__init__(gmi)

    def parse(self, response):
        return Group.from_json(self.gmi, response)

    def url(self):
        return self.base_url + "/groups/" + str(self.group_id) + '/update'

    def mode(self):
        return "POST"

    def args(self):
        arg_dict = {}
        if self.name is not None:
            arg_dict['name'] = self.name
        if self.description is not None:
            arg_dict['description'] = self.description
        if self.image_url is not None:
            arg_dict['image_url'] = self.image_url
        if self.office_mode is not None:
            arg_dict['office_mode'] = self.office_mode
        if self.share is not None:
            arg_dict['share'] = self.share
        return arg_dict


class GroupsDestroyRequest(Request):
    def __init__(self, gmi, group_id):
        self.group_id = group_id
        super().__init__(gmi)

    def parse(self, response):
        pass

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/destroy'

    def mode(self):
        return 'POST'


class GroupsJoinRequest(Request):
    def __init__(self, gmi, group_id, share_token):
        self.group_id = group_id
        self.share_token = share_token
        super().__init__(gmi)

    def parse(self, response):
        return Group.from_json(self.gmi, response)

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/join/' + str(self.share_token)

    def mode(self):
        return "POST"


class GroupsRejoinRequest(Request):
    def __init__(self, gmi, group_id):
        self.group_id = group_id
        super().__init__(gmi)

    def parse(self, response):
        return Group.from_json(self.gmi, response)

    def url(self):
        return self.base_url + '/groups/join'

    def mode(self):
        return "POST"

    def args(self):
        return {
            'group_id': self.group_id
        }
