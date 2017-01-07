class AbstractObject:
    field_map = {}  # This is a dict of keys to values using: AbstractObject.KEY = json[VALUE]

    def save(self):
        raise NotImplementedError

    def _refresh_from_other(self, other):
        for key, _ in self.field_map.items():
            setattr(self, key, getattr(other, key))
        self.on_fields_loaded()

    def on_fields_loaded(self):
        pass

    def refresh(self):
        raise NotImplementedError

    @staticmethod
    def get(gmi, *args):
        raise NotImplementedError

    @classmethod
    def from_json(cls, gmi, json_dict, *args):
        obj = cls(gmi, *args)

        for key, value_raw in obj.field_map.items():
            json_val = json_dict
            for val in value_raw.split('.'):
                json_val = json_val.get(val, None)
            setattr(obj, key, json_val)
        obj.on_fields_loaded()
        return obj