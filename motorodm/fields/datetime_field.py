from .field import Field
from datetime import datetime


class DateTimeField(Field):

    def validate(self, value):
        if value is not None:
            if not isinstance(value, datetime):
                return False

        return super().validate(value)
