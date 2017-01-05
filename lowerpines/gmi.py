import requests

_gmi_objects = []


def get_gmi(api_key):
    for gmi in _gmi_objects:
        if gmi.api_key == api_key:
            return gmi
    gmi = GMI(api_key)
    _gmi_objects.append(gmi)
    return gmi


class GMI:
    def __init__(self, api_key, cache=15):
        from lowerpines.group import GroupManager
        from lowerpines.bot import BotManager
        from lowerpines.user import UserManager

        self.api_key = api_key
        self.cache = cache
        self.groups = GroupManager(self)
        self.bots = BotManager(self)
        self.user = UserManager(self)

    def convert_image_url(self, url):
        from lowerpines.endpoints.image import ImageConvertRequest
        return ImageConvertRequest(self, requests.get(url).content).result

