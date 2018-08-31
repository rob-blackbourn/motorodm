from .field import Field


class FloatField(Field):

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        if value is not None:
            if not isinstance(value, float):
                return False

            if self.min_value is not None and value < self.min_value:
                return False

            if self.max_value is not None and value > self.max_value:
                return False

        return super().validate(value)

    def is_empty(self, value):
        return value is None
