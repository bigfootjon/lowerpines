# pyre-strict
from typing import TYPE_CHECKING, Dict, List, Union
from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message

if TYPE_CHECKING:
    from lowerpines.gmi import GMI
    from lowerpines.endpoints.group import Group


class Bot(AbstractObject, RetrievableObject):
    # pyre-ignore
    bot_id: str = Field()
    # pyre-ignore
    group_id: str = Field()
    # pyre-ignore
    name: str = Field()
    # pyre-ignore
    avatar_url: str = Field()
    # pyre-ignore
    callback_url: str = Field()
    # pyre-ignore
    dm_notification: str = Field()

    def __init__(
        self, gmi: "GMI", group_id: str, name: str, avatar_url: str, callback_url: str
    ) -> None:
        self.gmi = gmi
        self.group_id = group_id
        self.name = name
        self.avatar_url = avatar_url
        self.callback_url = callback_url

    @property
    def group(self) -> "Group":
        # pyre-ignore
        return self.gmi.groups.get(group_id=self.group_id)

    def save(self) -> None:
        if self.bot_id is None:
            new_data = BotCreateRequest(
                self.gmi,
                self.group_id,
                self.name,
                self.callback_url,
                self.avatar_url,
                self.dm_notification,
            ).result
            self._refresh_from_other(new_data)
        else:
            BotsUpdateRequest(
                self.gmi,
                self.bot_id,
                self.group_id,
                self.name,
                self.callback_url,
                self.avatar_url,
                self.dm_notification,
            )

    def delete(self) -> None:
        if self.bot_id is None:
            raise InvalidOperationException("Cannot destroy a bot that isn't saved!")
        else:
            BotDestroyRequest(self.gmi, self.bot_id)

    def refresh(self) -> None:
        if self.bot_id is None:
            raise InvalidOperationException("This operation is not permitted")
        else:
            raise InvalidOperationException("This is non trivial to implement")

    def post(self, text: str) -> None:
        text, attachments = smart_split_complex_message(text)
        BotPostRequest(self.gmi, self.bot_id, text, attachments)

    @staticmethod
    def get_all(gmi: "GMI") -> List["Bot"]:
        return BotIndexRequest(gmi).result

    @staticmethod
    def get(gmi: "GMI", bot_id: str) -> None:
        pass

    def __str__(self) -> str:
        return self.name + ":" + self.group_id


class BotCreateRequest(Request[Bot]):
    group_id: str
    name: str
    callback_url: str
    avatar_url: str
    dm_notification: str

    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        name: str,
        callback_url: str,
        avatar_url: str,
        dm_notification: str,
    ) -> None:
        self.name = name
        self.group_id = group_id
        self.dm_notification = dm_notification
        self.callback_url = callback_url
        self.avatar_url = avatar_url
        super().__init__(gmi)

    def parse(self, response: Dict[str, str]) -> Bot:
        return Bot.from_json(self.gmi, response["bot"])

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/bots"

    def args(self) -> Dict[str, Dict[str, str]]:
        post_dict = {"bot": {"name": self.name, "group_id": self.group_id}}
        if self.avatar_url is not None:
            post_dict["bot"]["avatar_url"] = self.avatar_url
        if self.callback_url is not None:
            post_dict["bot"]["callback_url"] = self.callback_url
        if self.dm_notification is not None:
            post_dict["bot"]["dm_notification"] = self.dm_notification
        return post_dict


class BotPostRequest(Request[None]):
    bot_id: str
    text: str
    attachments: List[Dict[str, Union[str, List[str]]]]

    def __init__(
        self,
        gmi: "GMI",
        bot_id: str,
        text: str,
        attachments: List[Dict[str, Union[str, List[str]]]],
    ) -> None:
        self.bot_id = bot_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response: str) -> None:
        return None

    def args(self) -> Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]:
        post_dict: Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]] = {
            "bot_id": self.bot_id,
            "text": str(self.text),
        }
        if self.attachments is not None:
            post_dict["attachments"] = self.attachments
        return post_dict

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/bots/post"


class BotIndexRequest(Request[List[Bot]]):
    def parse(self, response: str) -> List[Bot]:
        bots = []
        for bot_json in response:
            bots.append(Bot.from_json(self.gmi, bot_json))
        return bots

    def mode(self) -> str:
        return "GET"

    def url(self) -> str:
        return self.base_url + "/bots"


class BotDestroyRequest(Request[None]):
    bot_id: str

    def __init__(self, gmi: "GMI", bot_id: str) -> None:
        self.bot_id = bot_id
        super().__init__(gmi)

    def parse(self, response: str) -> None:
        return None

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/bots/destroy"

    def args(self) -> Dict[str, str]:
        return {"bot_id": self.bot_id}


# --- Undocumented ---


class BotsUpdateRequest(Request[None]):
    group_id: str
    name: str
    avatar_url: str
    callback_url: str
    dm_notification: str
    bot_id: str

    def __init__(
        self,
        gmi: "GMI",
        bot_id: str,
        group_id: str,
        name: str,
        callback_url: str,
        avatar_url: str,
        dm_notification: str,
    ) -> None:
        self.group_id = group_id
        self.name = name
        self.avatar_url = avatar_url
        self.callback_url = callback_url
        self.dm_notification = dm_notification
        self.bot_id = bot_id
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/bots/update"

    def mode(self) -> str:
        return "POST"

    def args(self) -> Dict[str, Dict[str, str]]:
        post_dict = {"bot": {"bot_id": self.bot_id}}
        if self.group_id is not None:
            post_dict["bot"]["group_id"] = self.group_id
        if self.name is not None:
            post_dict["bot"]["name"] = self.name
        if self.avatar_url is not None:
            post_dict["bot"]["avatar_url"] = self.avatar_url
        if self.callback_url is not None:
            post_dict["bot"]["callback_url"] = self.callback_url
        if self.dm_notification is not None:
            post_dict["bot"]["dm_notification"] = self.dm_notification
        if self.bot_id is not None:
            post_dict["bot"]["bot_id"] = self.bot_id
        return post_dict

    def parse(self, response: str) -> None:
        pass
