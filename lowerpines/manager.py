# pyre-strict
from typing import (
    Dict,
    Sized,
    TYPE_CHECKING,
    Union,
    List,
    Optional,
    Iterator,
    TypeVar,
    Generic,
)

from lowerpines.exceptions import NoneFoundException, MultipleFoundException

if TYPE_CHECKING:
    from lowerpines.gmi import GMI

T = TypeVar("T")


class AbstractManager(Sized, Generic[T]):
    _content: Optional[Union[List[T], T]]

    def __len__(self) -> int:
        self.lazy_fill_content()
        # pyre-ignore
        return self._content.__len__()

    def __getitem__(self, key: int) -> T:
        self.lazy_fill_content()
        # pyre-ignore
        return self._content.__getitem__(key)

    def __iter__(self) -> Iterator[T]:
        self.lazy_fill_content()
        # pyre-ignore
        return self._content.__iter__()

    def __init__(self, gmi: "GMI", content: Optional[Union[List[T], T]] = None) -> None:
        self.gmi = gmi
        self._content = content

    def _all(self):
        raise NotImplementedError

    def get(self, **kwargs: Dict[str, str]) -> T:
        filtered = self.filter(**kwargs)
        if len(filtered) == 0:
            raise NoneFoundException()
        elif len(filtered) == 1:
            return filtered[0]
        else:
            raise MultipleFoundException()

    def filter(self, **kwargs: Dict[str, str]) -> "AbstractManager[T]":
        self.lazy_fill_content()
        filtered = self._content
        for arg, value in kwargs.items():
            filtered = [item for item in filtered if getattr(item, arg) == value]
        return self.__class__(self.gmi, filtered)

    def lazy_fill_content(self) -> None:
        if self._content is None:
            self._content = self._all()
