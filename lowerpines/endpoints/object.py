# pyre-strict
from typing import Dict, TYPE_CHECKING, Type, List, Tuple, Optional, TypeVar, Any

from lowerpines.endpoints.request import JsonType

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI

T = TypeVar("T")


class Field:
    def __init__(self) -> None:
        self.name = ""
        self.api_name: Optional[str] = None

    def with_api_name(self, api_name: str) -> "Field":
        self.api_name = api_name
        return self

    def with_type(self, _: Type[T]) -> T:
        # This is intentional, it allows us to trick type-checkers into asserting that the field type is T,
        # which will be true at runtime, since Field types are erased by the metaclass
        return self  # type: ignore

    def with_field_name(self, name: str) -> "Field":
        self.name = name
        if self.api_name is None:
            self.api_name = name
        return self


class AbstractObjectType(type):
    def __new__(
        mcs,
        name: str,
        bases: Tuple[Type["AbstractObjectType"]],
        attrs: Dict[str, Field],
    ) -> Type["AbstractObjectType"]:
        new_attrs = {}  # type: ignore
        fields = []
        for attr_name, attr_value in attrs.items():
            if type(attr_value) == Field:
                attr_value.with_field_name(attr_name)
                fields.append(attr_value)
                new_attrs[attr_name] = None
            else:
                new_attrs[attr_name] = attr_value
        new_attrs["_fields"] = fields  # type: ignore

        # pyre-ignore
        return super(AbstractObjectType, mcs).__new__(mcs, name, bases, new_attrs)


TAbstractObject = TypeVar("TAbstractObject", bound="AbstractObject")


class AbstractObject(metaclass=AbstractObjectType):
    _fields: List[Field] = []

    def __init__(self, _: "GMI", *_args: JsonType) -> None:
        pass

    def _refresh_from_other(self, other: TAbstractObject) -> None:
        if other is not None:
            for field in self._fields:
                setattr(self, field.name, getattr(other, field.name))
        self.on_fields_loaded()

    def on_fields_loaded(self) -> None:
        pass

    @classmethod
    def from_json(
        cls: Type[TAbstractObject], gmi: "GMI", json_dict: JsonType, *args: Any
    ) -> TAbstractObject:
        # TODO Pull out args that are needed by constructor and use them here, removes a few pyre ignores
        obj = cls(gmi, *args)

        for field in obj._fields:
            json_val = json_dict
            api_name = field.api_name
            if api_name is None:  # pragma: no cover
                raise ValueError("api_name should be known by this point")
            for val in api_name.split("."):
                json_val = json_val.get(val, None)
            setattr(obj, field.name, json_val)
        obj.on_fields_loaded()
        return obj


class RetrievableObject:
    def save(self) -> None:
        raise NotImplementedError  # pragma: no cover

    def refresh(self) -> None:
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def get(gmi: "GMI", *args: JsonType) -> Type["RetrievableObject"]:
        raise NotImplementedError  # pragma: no cover
