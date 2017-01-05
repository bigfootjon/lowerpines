from lowerpines.endpoints import Request


class Member:
    member_id = None
    user_id = None
    nickname = None
    muted = None
    image_url = None
    autokicked = None

    group_id = None
    phone_number = None
    email = None

    def __init__(self, gmi, group_id, nickname=None, user_id=None, phone_number=None, email=None):
        self.gmi = gmi
        self.group_id = group_id
        self.nickname = nickname
        self.user_id = user_id
        self.phone_number = phone_number
        self.email = email

    def save(self):
        if self.member_id is None:
            if self.user_id is not None:
                MembersAddRequest(self.gmi, self.group_id, self.nickname, user_id=self.user_id)
            elif self.phone_number is not None:
                MembersAddRequest(self.gmi, self.group_id, self.nickname, phone_number=self.phone_number)
            elif self.email is not None:
                MembersAddRequest(self.gmi, self.group_id, self.nickname, email=self.email)
            else:
                raise Exception('Please define one of user_id, phone_number, email before saving')
        else:  # Only works for current user
            new_data = MembersUpdateRequest(self.gmi, self.group_id, self.nickname).result
            self._refresh_from_other(new_data)

    def _refresh_from_other(self, other):
        self.member_id = other.member_id
        self.user_id = other.user_id
        self.nickname = other.nickname
        self.muted = other.muted
        self.image_url = other.image_url
        self.autokicked = other.autokicked

        self.group_id = other.group_id
        self.phone_number = other.phone_number
        self.email = other.email

    @staticmethod
    def from_json(gmi, json, group_id):
        member = Member(gmi, group_id)

        member.member_id = json['id']
        member.user_id = json['user_id']
        member.nickname = json['nickname']
        member.muted = json['muted']
        member.image_url = json['image_url']
        member.autokicked = json['autokicked']

        return member

    def __str__(self):
        return self.nickname

    def __repr__(self):
        return str(self)


class MembersAddRequest(Request):
    def __init__(self, gmi, group_id, nickname, user_id=None, phone_number=None, email=None, guid=None):
        self.group_id = group_id
        self.nickname = nickname
        self.guid = guid

        self.user_id = user_id
        self.email = email
        self.phone_number = phone_number

        if user_id is None and email is not None and phone_number is not None:
            raise Exception('Must provide user_id, email, or phone_number')
        super().__init__(gmi)

    def url(self):
        return self.base_url + "/groups/" + str(self.group_id) + "/members/add"

    def args(self):
        add_dict = {
            'members': [
                {
                    'nickname': self.nickname,
                    'user_id': self.user_id
                }
            ]
        }
        return add_dict

    def mode(self):
        return "POST"

    def parse(self, response):
        return response['results_id']


# Not used
class MembersResultsRequest(Request):
    def __init__(self, gmi, group_id, results_id):
        self.group_id = group_id
        self.results_id = results_id
        super().__init__(gmi)

    def mode(self):
        return "GET"

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/members/results/' + str(self.results_id)

    def parse(self, response):
        members = []
        for member_json in response['members']:
            members.append(Member.from_json(self.gmi, member_json, self.group_id))
        return members


class MembersRemoveRequest(Request):
    def __init__(self, gmi, group_id, member_id):
        self.group_id = group_id
        self.member_id = member_id
        super().__init__(gmi)

    def mode(self):
        return "POST"

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/members/' + str(self.member_id) + '/remove'

    def parse(self, response):
        return None


class MembersUpdateRequest(Request):
    def __init__(self, gmi, group_id, nickname):
        self.group_id = group_id
        self.nickname = nickname
        super().__init__(gmi)

    def mode(self):
        return "POST"

    def url(self):
        return self.base_url + '/groups/' + str(self.group_id) + '/memberships/update'

    def args(self):
        return {
            'membership': {
                'nickname': self.nickname
            }
        }

    def parse(self, response):
        return Member.from_json(self.gmi, response, self.group_id)
