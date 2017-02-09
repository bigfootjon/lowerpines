import requests

_gmi_objects = []


def get_gmi(access_token):
    for gmi in _gmi_objects:
        if gmi.access_token == access_token:
            return gmi
    gmi = GMI(access_token)
    _gmi_objects.append(gmi)
    return gmi


class GMI:
    def __init__(self, access_token):
        self.access_token = access_token

        self.groups = None
        self.bots = None
        self.chats = None
        self.user = None

        self.refresh()

    def refresh(self):
        from lowerpines.group import GroupManager
        from lowerpines.bot import BotManager
        from lowerpines.chat import ChatManager
        from lowerpines.user import UserManager

        self.groups = GroupManager(self)
        self.bots = BotManager(self)
        self.chats = ChatManager(self)
        self.user = UserManager(self)

    def convert_image_url(self, url):
        from lowerpines.endpoints.image import ImageConvertRequest
        return ImageConvertRequest(self, requests.get(url).content).result

