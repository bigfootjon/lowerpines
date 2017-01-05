from lowerpines.endpoints.user import User


class UserManager:
    def __init__(self, gmi):
        self.gmi = gmi

    def get(self):
        return User.get(self.gmi)
