import importlib

"""
    Design proposal:
Map (object, operation) pair to a specific query to be run.
Repository name will be <model_class_name>Repository so the model name
can be extracted.
"""


class Repository:
    def __init__(self) -> None:
        if type(self) == Repository:
            raise ValueError("Do not instantiate base Repository!")

        # XxxRepository => Repository
        self._class_name = self.__class__.__name__[
            : self.__class__.__name__.rfind("Repository")
        ]

        # The model class can be instantiated if needed (obj = self._class())
        self._class = getattr(importlib.import_module("models"), self._class_name)

    def save(self, obj):
        raise NotImplementedError()

    def fetch_all(self):
        raise NotImplementedError()

    def search_by_id(self, id):
        raise NotImplementedError()

    def search_by_attributes(self, attributes):
        raise NotImplementedError()

    def delete(self, id):
        raise NotImplementedError()

    def __iter__(self):
        return iter(self.fetch_all())
