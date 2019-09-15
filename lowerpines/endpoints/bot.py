# pyre-strict
from typing import TYPE_CHECKING, Optional, List, Union

from lowerpines.endpoints.message import AttachmentType
from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request, JsonType
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI
    from lowerpines.message import ComplexMessage  # noqa: F401
    from lowerpines.endpoints.group import Group


class Bot(AbstractObject, RetrievableObject):
    bot_id: str = Field().with_type(str)
    group_id: str = Field().with_type(str)
    name: str = Field().with_type(str)
    avatar_url: Optional[str] = Field().with_type(str)
    callback_url: Optional[str] = Field().with_type(str)
    dm_notification: Optional[bool] = Field().with_type(bool)

    def __init__(
        self,
        gmi: "GMI",
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        callback_url: Optional[str] = None,
        dm_notification: Optional[bool] = None,
    ) -> None:
        self.gmi = gmi
        self.group_id = group_id  # type: ignore
        self.name = name  # type: ignore
        self.avatar_url = avatar_url
        self.callback_url = callback_url
        self.dm_notification = dm_notification

    @property
    def group(self) -> "Group":
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
            BotUpdateRequest(
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

    def post(self, message: Union["ComplexMessage", str]) -> None:
        text, attachments = smart_split_complex_message(message)
        BotPostRequest(self.gmi, self.bot_id, text, attachments)

    @staticmethod
    def get_all(gmi: "GMI") -> List["Bot"]:
        return BotIndexRequest(gmi).result

    @staticmethod
    def get(gmi: "GMI", bot_id: str) -> None:  # type: ignore
        raise InvalidOperationException("This is non trivial to implement")

    def __str__(self) -> str:
        return self.name + ":" + self.group_id


class BotCreateRequest(Request[Bot]):
    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        name: str,
        callback_url: Optional[str] = None,
        avatar_url: Optional[str] = None,
        dm_notification: Optional[bool] = None,
    ) -> None:
        self.name = name
        self.group_id = group_id
        self.dm_notification = dm_notification
        self.callback_url = callback_url
        self.avatar_url = avatar_url
        super().__init__(gmi)

    def parse(self, response: JsonType) -> Bot:
        return Bot.from_json(self.gmi, response["bot"])

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/bots"

    def args(self) -> JsonType:
        post_dict: JsonType = {"bot": {"name": self.name, "group_id": self.group_id}}
        avatar_url = self.avatar_url
        if avatar_url is not None:
            post_dict["bot"]["avatar_url"] = avatar_url
        callback_url = self.callback_url
        if callback_url is not None:
            post_dict["bot"]["callback_url"] = callback_url
        dm_notification = self.dm_notification
        if dm_notification is not None:
            post_dict["bot"]["dm_notification"] = dm_notification
        return post_dict


class BotPostRequest(Request[None]):
    def __init__(
        self,
        gmi: "GMI",
        bot_id: str,
        text: str,
        attachments: Optional[List[AttachmentType]] = None,
    ) -> None:
        self.bot_id = bot_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response: JsonType) -> None:
        return None

    def args(self) -> JsonType:
        post_dict = {"bot_id": self.bot_id, "text": str(self.text)}
        if self.attachments is not None:
            post_dict["attachments"] = self.attachments  # type: ignore
        return post_dict

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/bots/post"


class BotIndexRequest(Request[List[Bot]]):
    def parse(self, response: JsonType) -> List[Bot]:
        bots = []
        for bot_json in response:
            bots.append(Bot.from_json(self.gmi, bot_json))  # type: ignore
        return bots

    def mode(self) -> str:
        return "GET"

    def url(self) -> str:
        return self.base_url + "/bots"


class BotDestroyRequest(Request[None]):
    def __init__(self, gmi: "GMI", bot_id: str) -> None:
        self.bot_id = bot_id
        super().__init__(gmi)

    def parse(self, response: JsonType) -> None:
        return None

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/bots/destroy"

    def args(self) -> JsonType:
        return {"bot_id": self.bot_id}


# --- Undocumented ---


class BotUpdateRequest(Request[None]):
    def __init__(
        self,
        gmi: "GMI",
        bot_id: str,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        callback_url: Optional[str] = None,
        avatar_url: Optional[str] = None,
        dm_notification: Optional[bool] = None,
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

    def args(self) -> JsonType:
        post_dict: JsonType = {"bot": {"bot_id": self.bot_id}}
        group_id = self.group_id
        if group_id is not None:
            post_dict["bot"]["group_id"] = group_id
        name = self.name
        if name is not None:
            post_dict["bot"]["name"] = name
        avatar_url = self.avatar_url
        if avatar_url is not None:
            post_dict["bot"]["avatar_url"] = avatar_url
        callback_url = self.callback_url
        if callback_url is not None:
            post_dict["bot"]["callback_url"] = callback_url
        dm_notification = self.dm_notification
        if dm_notification is not None:
            post_dict["bot"]["dm_notification"] = dm_notification
        bot_id = self.bot_id
        if bot_id is not None:
            post_dict["bot"]["bot_id"] = bot_id
        return post_dict

    def parse(self, response: JsonType) -> None:
        pass
