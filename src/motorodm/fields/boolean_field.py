from .field import Field


class BooleanField(Field):

    def validate(self, value):
        if value is not None:
            if not isinstance(value, bool):
                return False

        return super().validate(value)
