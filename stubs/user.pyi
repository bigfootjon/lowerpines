from lowerpines.endpoints.user import User
from lowerpines.gmi import GMI


class UserManager:
    gmi = ... #  type: GMI

    def __init__(self, gmi: GMI) -> None: ...
    def get(self) -> User: ...
