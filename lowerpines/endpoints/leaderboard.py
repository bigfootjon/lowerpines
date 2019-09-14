# pyre-strict
from typing import List, TYPE_CHECKING

from lowerpines.endpoints.request import Request, JsonType
from lowerpines.endpoints.message import Message

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI


class Leaderboard:
    def __init__(self, gmi: "GMI", group_id: str) -> None:
        self.gmi = gmi
        self.group_id = group_id

    def _for_period(self, period: str) -> List[Message]:
        return LeaderboardIndexRequest(self.gmi, self.group_id, period).result

    def for_today(self) -> List[Message]:
        return self._for_period("day")

    def for_week(self) -> List[Message]:
        return self._for_period("week")

    def for_month(self) -> List[Message]:
        return self._for_period("month")

    def my_likes(self) -> List[Message]:
        return LeaderboardMyLikesRequest(self.gmi, self.group_id).result

    def my_hits(self) -> List[Message]:
        return LeaderboardMyHitsRequest(self.gmi, self.group_id).result


class LeaderboardIndexRequest(Request[List[Message]]):
    def __init__(self, gmi: "GMI", group_id: str, period: str) -> None:
        self.group_id = group_id
        if period not in ["day", "week", "month"]:
            raise ValueError("Period must be one of: day, week, or month")
        self.period = period
        super().__init__(gmi)

    def parse(self, response: JsonType) -> List[Message]:
        messages = []
        for message_json in response["messages"]:
            messages.append(Message.from_json(self.gmi, message_json))
        return messages

    def url(self) -> str:
        return self.base_url + "/groups/" + self.group_id + "/likes"

    def mode(self) -> str:
        return "GET"


class LeaderboardMyLikesRequest(Request[List[Message]]):
    def __init__(self, gmi: "GMI", group_id: str) -> None:
        self.group_id = group_id
        super().__init__(gmi)

    def parse(self, response: JsonType) -> List[Message]:
        messages = []
        for message_json in response["messages"]:
            messages.append(Message.from_json(self.gmi, message_json))
        return messages

    def url(self) -> str:
        return self.base_url + "/groups/" + self.group_id + "/likes/mine"

    def mode(self) -> str:
        return "GET"


class LeaderboardMyHitsRequest(Request[List[Message]]):
    def __init__(self, gmi: "GMI", group_id: str) -> None:
        self.group_id = group_id
        super().__init__(gmi)

    def parse(self, response: JsonType) -> List[Message]:
        messages = []
        for message_json in response["messages"]:
            messages.append(Message.from_json(self.gmi, message_json))
        return messages

    def url(self) -> str:
        return self.base_url + "/groups/" + self.group_id + "/likes/for_me"

    def mode(self) -> str:
        return "GET"
