from .field import Field


class StringField(Field):

    def __init__(self, max_length=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_length = max_length

    def validate(self, value):
        if value is not None:
            if not isinstance(value, str):
                return False

            if self.max_length is not None and len(value) > self.max_length:
                return False

        return super().validate(value)

    def is_empty(self, value):
        return value is None or value == ""
