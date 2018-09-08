from .field import Field


class StringField(Field):

    def __init__(self, regex=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = regex

    def validate(self, value):
        if value is not None:
            if not isinstance(value, str):
                return False

            if self.regex and not self.regex.match(value):
                return False

        return super().validate(value)

    def is_empty(self, value):
        return value is None or value == ""
