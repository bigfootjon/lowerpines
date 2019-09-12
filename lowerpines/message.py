# pyre-strict
from typing import Union, Tuple, List, Dict

from lowerpines.endpoints.message import Message
from lowerpines.gmi import GMI


class MessageManager:
    def __init__(self, gmi: GMI) -> None:
        self.gmi = gmi

    def get(self, group_id: str, message_id: str) -> Message:
        return Message.get(self.gmi, group_id, message_id)


class MessageAttach:
    def __add__(
        self, other: Union["ComplexMessage", "MessageAttach", str]
    ) -> "ComplexMessage":
        if isinstance(other, ComplexMessage):
            other.contents.append(self)
            return other
        else:
            return ComplexMessage([self, other])

    def __radd__(
        self, other: Union["ComplexMessage", "MessageAttach", str]
    ) -> "ComplexMessage":
        if isinstance(other, ComplexMessage):
            other.contents.append(self)
            return other
        else:
            return ComplexMessage([other, self])


class RefAttach(MessageAttach):
    def __init__(self, user_id: str, display: str = "") -> None:
        self.display = display
        self.user_id = user_id

    def __str__(self) -> str:
        return self.display

    def __repr__(self) -> str:
        return "R:" + self.display


class ImageAttach(MessageAttach):
    def __init__(self, image_url: str) -> None:
        self.image_url = image_url

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:
        return "I:" + str(self)


class LocationAttach(MessageAttach):
    def __init__(self, name: str, lat: str, long: str) -> None:
        self.name = name
        self.lat = lat
        self.long = long

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "L:" + str(self)


# This feature is not supported anymore but it still exists in the API
class SplitAttach(MessageAttach):
    def __init__(self, token: str) -> None:
        self.token = token

    def __str__(self) -> str:
        return self.token

    def __repr__(self) -> str:
        return "S:" + str(self)


EMOJI_PLACEHOLDER = "\ufffd"


class EmojiAttach(MessageAttach):
    def __init__(self, pack_id: str, emoji_id: str) -> None:
        self.pack_id = pack_id
        self.emoji_id = emoji_id

    def __str__(self) -> str:
        return EMOJI_PLACEHOLDER

    def __repr__(self) -> str:
        return "E:" + str(self)


# Undocumented feature
class QueuedAttach(MessageAttach):
    def __init__(self, url: str, queue: str) -> None:
        self.url = url
        self.queue = queue

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return "Q: " + str(self)


class LinkedImageAttach(QueuedAttach):
    def __init__(self, url: str) -> None:
        super().__init__(url, "linked_image")


class ComplexMessage:
    contents: List[Union[str, MessageAttach]]

    def __init__(self, data: Union[List[Union[str, MessageAttach]], str]) -> None:
        if isinstance(data, list):
            self.contents = data
        else:
            self.contents = [data]

    def __add__(
        self, other: Union["ComplexMessage", MessageAttach, str]
    ) -> "ComplexMessage":
        if isinstance(other, self.__class__):
            self.contents.extend(other.contents)
        else:
            self.contents.append(other)
        return self

    def __radd__(
        self, other: Union["ComplexMessage", MessageAttach, str]
    ) -> "ComplexMessage":
        if isinstance(other, self.__class__):
            self.contents = other.contents + self.contents
        else:
            self.contents.insert(0, other)
        return self

    def __str__(self) -> str:
        return str(self.contents)

    def get_text(self) -> str:
        return "".join([str(part) for part in self.contents])

    def get_attachments(self) -> List[Dict[str, Union[str, List[str]]]]:
        attach_list = []
        mentions = {"type": "mentions", "user_ids": list(), "loci": list()}
        emojis = {"type": "emoji", "placeholder": EMOJI_PLACEHOLDER, "charmap": []}
        queued = {"type": "postprocessing", "queues": []}
        content_frag = ""
        for part in self.contents:
            if isinstance(part, RefAttach):
                # pyre-ignore
                mentions["user_ids"].append(part.user_id)
                mentions["loci"].append([len(content_frag), len(part.display)])
                if mentions not in attach_list:
                    attach_list.append(mentions)
            elif isinstance(part, ImageAttach):
                attach_list.append({"type": "image", "url": part.image_url})
            elif isinstance(part, LocationAttach):
                attach_list.append(
                    {
                        "type": "location",
                        "name": part.name,
                        "lat": part.lat,
                        "long": part.long,
                    }
                )
            elif isinstance(part, SplitAttach):
                attach_list.append({"type": "split", "token": part.token})
            elif isinstance(part, EmojiAttach):
                emojis["charmap"].append([part.pack_id, part.emoji_id])
                if emojis not in attach_list:
                    attach_list.append(emojis)
            elif isinstance(part, QueuedAttach):
                if part.queue not in queued["queues"]:
                    queued["queues"].append(part.queue)
                if queued not in attach_list:
                    attach_list.append(queued)
            content_frag += str(part)
        return attach_list

    def just_str(self) -> str:
        return "".join([s for s in self.contents if isinstance(s, str)])


def smart_split_complex_message(
    message: Union["ComplexMessage", str]
) -> Tuple[str, List[Dict[str, Union[str, List[str]]]]]:
    if isinstance(message, ComplexMessage):
        return message.get_text(), message.get_attachments()
    elif isinstance(message, str):
        return message, []
    else:
        raise ValueError("Message object must be a str or ComplexMessage")
