from lowerpines.endpoints.user import User
from lowerpines.manager import AbstractManager


class UserManager(AbstractManager):
    def _all(self):
        return [User.get(self.gmi)]
