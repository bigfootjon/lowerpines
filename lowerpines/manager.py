# pyre-strict
from typing import List, TypeVar, Generic, Iterator, Optional, TYPE_CHECKING, Any

from lowerpines.exceptions import NoneFoundException, MultipleFoundException

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI

T = TypeVar("T")


class AbstractManager(Generic[T]):
    def __len__(self) -> int:
        content = self.lazy_fill_content()
        return content.__len__()

    def __getitem__(self, key: int) -> T:
        content = self.lazy_fill_content()
        return content.__getitem__(key)

    def __iter__(self) -> Iterator[T]:
        content = self.lazy_fill_content()
        return content.__iter__()

    def __init__(self, gmi: "GMI", content: Optional[List[T]] = None) -> None:
        self.gmi = gmi
        self._content = content

    def _all(self) -> List[T]:
        raise NotImplementedError  # pragma: no cover

    def get(self, **kwargs: Any) -> T:
        filtered = self.filter(**kwargs)
        if len(filtered) == 0:
            raise NoneFoundException()
        elif len(filtered) == 1:
            return filtered[0]
        else:
            raise MultipleFoundException()

    def filter(self, **kwargs: Any) -> "AbstractManager[T]":
        self.lazy_fill_content()
        filtered = self._content
        for arg, value in kwargs.items():
            filtered = [
                item for item in filtered if getattr(item, arg) == value  # type: ignore
            ]
        return self.__class__(self.gmi, filtered)

    def lazy_fill_content(self) -> List[T]:
        if self._content is None:
            self._content = self._all()
        return self._content
