from lowerpines.exceptions import NoneFoundException, MultipleFoundException


class AbstractManager:
    def __len__(self):
        self.lazy_fill_content()
        return self._content.__len__()

    def __getitem__(self, key):
        self.lazy_fill_content()
        return self._content.__getitem__(key)

    def __iter__(self):
        self.lazy_fill_content()
        return self._content.__iter__()

    def __init__(self, gmi, content=None):
        self.gmi = gmi
        self._content = content

    def _all(self):
        raise NotImplementedError

    def get(self, **kwargs):
        filtered = self.filter(**kwargs)
        if len(filtered) == 0:
            raise NoneFoundException()
        elif len(filtered) == 1:
            return filtered[0]
        else:
            raise MultipleFoundException()

    def filter(self, **kwargs):
        self.lazy_fill_content()
        filtered = self._content
        for arg, value in kwargs.items():
            filtered = [item for item in filtered if getattr(item, arg) == value]
        return self.__class__(self.gmi, filtered)

    def lazy_fill_content(self):
        if self._content is None:
            self._content = self._all()
