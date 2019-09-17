# pyre-strict
from typing import Union, List, Tuple, Dict


class MessageAttach:
    def __add__(
        self, other: Union["ComplexMessage", str, "MessageAttach"]
    ) -> "ComplexMessage":
        if isinstance(other, ComplexMessage):
            other.contents.insert(0, self)
            return other
        else:
            return ComplexMessage([self, other])

    def __radd__(self, other: Union[str, "MessageAttach"]) -> "ComplexMessage":
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
    def __init__(self, name: str, lat: int, long: int) -> None:
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
    def __init__(self, pack_id: int, emoji_id: int) -> None:
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
    contents: List[Union[MessageAttach, str]]

    # pyre-ignore
    def __init__(self, data: Union[list, str, MessageAttach]) -> None:
        if isinstance(data, list):
            self.contents = data
        elif isinstance(data, str):
            self.contents = [data]

    def __add__(
        self, other: Union["ComplexMessage", str, "MessageAttach"]
    ) -> "ComplexMessage":
        if isinstance(other, self.__class__):
            self.contents.extend(other.contents)
        else:
            self.contents.append(other)  # type: ignore
        return self

    def __radd__(
        self, other: Union["ComplexMessage", str, "MessageAttach"]
    ) -> "ComplexMessage":
        self.contents.insert(0, other)  # type: ignore
        return self

    def __str__(self) -> str:
        return str(self.contents)

    def get_text(self) -> str:
        return "".join([str(part) for part in self.contents])

    def get_attachments(self) -> List[Dict[str, str]]:
        attach_list = []  # type: ignore
        mentions = {"type": "mentions", "user_ids": list(), "loci": list()}
        emojis = {"type": "emoji", "placeholder": EMOJI_PLACEHOLDER, "charmap": []}
        queued = {"type": "postprocessing", "queues": []}
        content_frag = ""
        for part in self.contents:
            if isinstance(part, RefAttach):
                # pyre-ignore
                mentions["user_ids"].append(part.user_id)  # type: ignore
                mentions["loci"].append(  # type: ignore
                    [len(content_frag), len(part.display)]
                )
                if mentions not in attach_list:
                    attach_list.append(mentions)
            elif isinstance(part, ImageAttach):
                attach_list.append({"type": "image", "url": part.image_url})
            elif isinstance(part, LocationAttach):
                attach_list.append(
                    {  # type: ignore
                        "type": "location",
                        "name": part.name,
                        "lat": part.lat,
                        "long": part.long,
                    }
                )
            elif isinstance(part, SplitAttach):
                attach_list.append({"type": "split", "token": part.token})
            elif isinstance(part, EmojiAttach):
                emojis["charmap"].append([part.pack_id, part.emoji_id])  # type: ignore
                if emojis not in attach_list:
                    attach_list.append(emojis)
            elif isinstance(part, QueuedAttach):
                if part.queue not in queued["queues"]:
                    queued["queues"].append(part.queue)  # type: ignore
                if queued not in attach_list:
                    attach_list.append(queued)
            content_frag += str(part)
        return attach_list  # type: ignore

    def just_str(self) -> str:
        return "".join([s for s in self.contents if isinstance(s, str)])


def smart_split_complex_message(
    message: Union[ComplexMessage, str]
) -> Tuple[str, List[Dict[str, str]]]:
    if isinstance(message, ComplexMessage):
        return message.get_text(), message.get_attachments()
    elif isinstance(message, str):
        return message, []
    else:
        raise ValueError("Message object must be a str or ComplexMessage")
