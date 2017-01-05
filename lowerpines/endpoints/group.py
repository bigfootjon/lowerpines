from lowerpines.endpoints import Request
from lowerpines.endpoints.member import MembersAddRequest, MembersRemoveRequest, Member


class Group:
    group_id = str()
    type = str()
    creator_user_id = str()
    created_at = str()
    updated_at = str()
    members = list()
    share_url = str()

    def __init__(self, gmi, name=None, description=None, image_url=None):
        self.gmi = gmi
        self.messages = GroupMessagesManager(self)
        self.name = name
        self.description = description
        self.image_url = image_url

    @property
    def bots(self):
        return self.gmi.bots.filter(group_id=self.group_id)

    @classmethod
    def from_json(cls, gmi, json):
        g = cls(gmi)

        g.group_id = json["id"]
        g.name = json["name"]
        g.type = json['type']
        g.description = json['description']
        g.image_url = json['image_url']
        g.creator_user_id = json['creator_user_id']
        g.created_at = json['created_at']
        g.updated_at = json['updated_at']
        for member_json in json['members']:
            g.members.append(Member.from_json(gmi, member_json, g.group_id))
        g.share_url = json['share_url']
        g.messages.count = json['messages']['count']
        g.messages.last_id = json['messages']['last_message_id']
        g.messages.last_created_at = json['messages']['last_message_created_at']

        return g

    def save(self):
        if self.group_id is None:
            new_data = GroupsCreateRequest(self.gmi, self.name, self.description, self.image_url).result
        else:
            new_data = GroupsUpdateRequest(self.gmi, self.group_id, self.name, self.description, self.image_url).result

        self._refresh_from_other(new_data)

    def delete(self):
        if self.group_id is None:
            raise Exception('Cannot destroy a group that isn\'t saved!')
        else:
            GroupsDestroyRequest(self.gmi, self.group_id)

    def _refresh_from_other(self, other_group):
        self.group_id = other_group.group_id
        self.name = other_group.name
        self.type = other_group.type
        self.description = other_group.description
        self.image_url = other_group.image_url
        self.creator_user_id = other_group.creator_user_id
        self.created_at = other_group.created_at
        self.updated_at = other_group.updated_at
        self.members = other_group.members
        self.share_url = other_group.share_url
        self.messages = other_group.messages

    def refresh(self):
        if self.group_id is None:
            raise Exception('Must have an id to perform this operation')
        else:
            new_data = GroupsShowRequest(self.gmi, group_id=self.group_id).result
            self._refresh_from_other(new_data)

    def member_add(self, name, user_id):
        MembersAddRequest(self.gmi, self.group_id, name, user_id=user_id)

    def member_rm(self, member_id):
        MembersRemoveRequest(self.gmi, self.group_id, member_id)

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
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count, before_id=message.message_id).result

    def since(self, message, count=100):
        from lowerpines.endpoints.message import MessagesIndexRequest
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count, since_id=message.message_id).result

    def after(self, message, count=100):
        from lowerpines.endpoints.message import MessagesIndexRequest
        return MessagesIndexRequest(self.group.gmi, self.group.group_id, limit=count, after_id=message.message_id).result


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
