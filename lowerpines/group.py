from lowerpines.manager import AbstractManager
from lowerpines.endpoints.group import Group


class GroupManager(AbstractManager):
    def _all(self):
        return Group.get_all(self.gmi)

    def former(self):
        return GroupManager(self.gmi, Group.get_former(self.gmi))

    def join(self, group_id, share_token):
        return Group.join(self.gmi, group_id, share_token)

    def rejoin(self, group_id):
        return Group.rejoin(self.gmi, group_id)
