from typing import Any, TYPE_CHECKING, List, Dict, Type, Optional

if TYPE_CHECKING:
    from lowerpines.gmi import GMI


class Field:
    def __init__(self, api_name: Optional[str] = None) -> None:
        self.name = ""
        self.api_name = api_name

    def set_name(self, name: str) -> None:
        self.name = name
        if self.api_name is None:
            self.api_name = name


class AbstractObjectType(type):
    def __new__(
        mcs, name: str, bases: Any, attrs: Dict[Any]
    ) -> Type["AbstractObjectType"]:
        new_attrs = {}
        fields = []
        for attr_name, attr_value in attrs.items():
            if type(attr_value) == Field:
                attr_value.set_name(attr_name)
                fields.append(attr_value)
                new_attrs[attr_name] = None
            else:
                new_attrs[attr_name] = attr_value
        new_attrs["_fields"] = fields

        # pyre-ignore
        return super(AbstractObjectType, mcs).__new__(mcs, name, bases, new_attrs)


class AbstractObject(metaclass=AbstractObjectType):
    _fields: List[Field] = []

    def __init__(self, _: "GMI", *args: Any) -> None:
        pass

    def _refresh_from_other(self, other: "AbstractObject") -> None:
        if other is not None:
            for field in self._fields:
                setattr(self, field.name, getattr(other, field.name))
        self.on_fields_loaded()

    def on_fields_loaded(self) -> None:
        pass

    @classmethod
    def from_json(cls, gmi: "GMI", json_dict: Any, *args: Any) -> Any:
        obj = cls(gmi, *args)

        for field in obj._fields:
            json_val = json_dict
            # pyre-ignore
            for val in field.api_name.split("."):
                json_val = json_val.get(val, None)
            setattr(obj, field.name, json_val)
        obj.on_fields_loaded()
        return obj


class RetrievableObject:
    def save(self) -> None:
        raise NotImplementedError

    def refresh(self) -> None:
        raise NotImplementedError

    @staticmethod
    def get(gmi: "GMI", *args: Any) -> Any:
        raise NotImplementedError
