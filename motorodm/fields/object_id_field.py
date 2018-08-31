from .field import Field


class ObjectIdField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
