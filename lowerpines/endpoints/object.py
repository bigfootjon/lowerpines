class Field:
    def __init__(self, handler=str, api_name=None):
        self.name = ''
        self.handler = handler
        self.api_name = api_name

    def set_name(self, name):
        self.name = name
        if self.api_name is None:
            self.api_name = name


class AbstractObjectType(type):
    def __new__(mcs, name, bases, attrs):
        new_attrs = {}
        fields = []
        for attr_name, attr_value in attrs.items():
            if type(attr_value) == Field:
                attr_value.set_name(attr_name)
                fields.append(attr_value)
                if attr_value.handler is None:
                    new_attrs[attr_name] = None
                else:
                    new_attrs[attr_name] = attr_value.handler()
            else:
                new_attrs[attr_name] = attr_value
        new_attrs['_fields'] = fields

        return super(AbstractObjectType, mcs).__new__(mcs, name, bases, new_attrs)


class AbstractObject(metaclass=AbstractObjectType):
    _fields = []

    def _refresh_from_other(self, other):
        for field in self._fields:
            setattr(self, field.name, getattr(other, field.name))
        self.on_fields_loaded()

    def on_fields_loaded(self):
        pass

    @classmethod
    def from_json(cls, gmi, json_dict, *args):
        obj = cls(gmi, *args)

        for field in obj._fields:
            json_val = json_dict
            for val in field.api_name.split('.'):
                json_val = json_val.get(val, None)
            if field.handler is not None:
                handled_val = field.handler(json_val)
            else:
                handled_val = json_val
            setattr(obj, field.name, handled_val)
        obj.on_fields_loaded()
        return obj


class RetrievableObject:
    def save(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError

    @staticmethod
    def get(gmi, *args):
        raise NotImplementedError
