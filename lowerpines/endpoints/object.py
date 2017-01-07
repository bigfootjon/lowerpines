class Field:
    def __init__(self, name=None, klass=str, api_name=None):
        self.name = name
        self.klass = klass
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
                new_attrs[attr_name] = attr_value.klass()
            else:
                new_attrs[attr_name] = attr_value
        new_attrs['_fields'] = fields

        return super(AbstractObjectType, mcs).__new__(mcs, name, bases, new_attrs)


class AbstractObject(metaclass=AbstractObjectType):
    field_map = {}  # This is a dict of keys to values using: AbstractObject.KEY = json[VALUE]
    _fields = []

    def save(self):
        raise NotImplementedError

    def _refresh_from_other(self, other):
        for field in self.get_fields():
            setattr(self, field.name, getattr(other, field.name))
        self.on_fields_loaded()

    def on_fields_loaded(self):
        pass

    def refresh(self):
        raise NotImplementedError

    def get_fields(self):
        if len(self.field_map) == 0:
            return self._fields
        else:
            fields_converted = []
            for attr_name, api_name in self.field_map.items():
                field = Field(api_name=api_name)
                field.set_name(attr_name)
                fields_converted.append(field)
            return fields_converted

    @staticmethod
    def get(gmi, *args):
        raise NotImplementedError

    @classmethod
    def from_json(cls, gmi, json_dict, *args):
        obj = cls(gmi, *args)

        for field in obj.get_fields():
            json_val = json_dict
            for val in field.api_name.split('.'):
                json_val = json_val.get(val, None)
            setattr(obj, field.name, json_val)
        obj.on_fields_loaded()
        return obj
