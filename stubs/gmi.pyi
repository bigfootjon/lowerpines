from typing import List

from lowerpines.bot import BotManager
from lowerpines.group import GroupManager
from lowerpines.user import UserManager

_gmi_objects = ... #  type: List[GMI]


def get_gmi(api_key: str) -> 'GMI': ...


class GMI:
    api_key = ... #  type: str
    cache = ... #  type: int
    groups = ... #  type: GroupManager
    bots = ... #  type: BotManager
    user = ... #  type: UserManager

    def __init__(self, api_key: str, cache: int=15) -> None: ...
    def convert_image_url(self, url: str) -> str: ...

