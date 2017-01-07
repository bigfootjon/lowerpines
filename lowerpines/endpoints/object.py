class Field:
    def __init__(self, klass=str, api_name=None):
        self.api_name = api_name
        self.klass = klass
        self.name = None

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
                new_attrs[attr_name] = attr_value.klass()
            else:
                new_attrs[attr_name] = attr_value
        new_attrs['_fields'] = fields

        return super(AbstractObjectType, mcs).__new__(mcs, name, bases, new_attrs)


class AbstractObject(metaclass=AbstractObjectType):
    field_map = {}  # This is a dict of keys to values using: AbstractObject.KEY = json[VALUE]

    def save(self):
        raise NotImplementedError

    def _refresh_from_other(self, other):
        for key, _ in self.get_fields():
            setattr(self, key, getattr(other, key))
        self.on_fields_loaded()

    def on_fields_loaded(self):
        pass

    def refresh(self):
        raise NotImplementedError

    def get_fields(self):
        return self.field_map.items()

    @staticmethod
    def get(gmi, *args):
        raise NotImplementedError

    @classmethod
    def from_json(cls, gmi, json_dict, *args):
        obj = cls(gmi, *args)

        for key, value_raw in obj.get_fields():
            json_val = json_dict
            for val in value_raw.split('.'):
                json_val = json_val.get(val, None)
            setattr(obj, key, json_val)
        obj.on_fields_loaded()
        return obj
