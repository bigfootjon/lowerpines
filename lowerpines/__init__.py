VERSION = '0.1.1'


class AbstractManager:
    def __len__(self):
        return self._content.__len__()

    def __getitem__(self, key):
        return self._content.__getitem__(key)

    def __delitem__(self, key):
        self._content.__delitem__(key)

    def __setitem__(self, key, value):
        self._content.__setitem__(key, value)

    def __iter__(self):
        return self._content.__iter__()

    def __init__(self, gmi, content=None):
        self.gmi = gmi
        if content is None:
            content = self._all()
        self._content = content

    def _all(self):
        raise NotImplementedError

    def get(self, **kwargs):
        filtered = self.filter(**kwargs)
        if len(filtered) == 0:
            raise Exception('None found')
        elif len(filtered) == 1:
            return filtered[0]
        else:
            raise Exception('Too many found')

    def filter(self, **kwargs):
        filtered = self._content
        for arg, value in kwargs.items():
            filtered = [item for item in filtered if getattr(item, arg) == value]
        return filtered
