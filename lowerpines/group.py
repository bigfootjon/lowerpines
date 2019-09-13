# pyre-strict

from typing import List

from lowerpines.manager import AbstractManager
from lowerpines.endpoints.group import Group


class GroupManager(AbstractManager[Group]):
    def _all(self) -> List[Group]:
        return Group.get_all(self.gmi)

    def former(self) -> "GroupManager":
        return GroupManager(self.gmi, Group.get_former(self.gmi))

    def join(self, group_id: str, share_token: str) -> Group:
        return Group.join(self.gmi, group_id, share_token)

    def rejoin(self, group_id: str) -> Group:
        return Group.rejoin(self.gmi, group_id)
