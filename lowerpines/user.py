# pyre-strict

from typing import List

from lowerpines.endpoints.user import User
from lowerpines.manager import AbstractManager


class UserManager(AbstractManager[User]):
    def _all(self) -> List[User]:
        return [User.get(self.gmi)]
