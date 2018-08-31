import decimal
from .field import Field


class DecimalField(Field):

    def __init__(self, min_value=None, max_value=None, precision=2, rounding=decimal.ROUND_HALF_UP, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_value = min_value
        if self.min_value is not None:
            self.min_value = decimal.Decimal(min_value)

        self.max_value = max_value
        if self.max_value is not None:
            self.max_value = decimal.Decimal(max_value)

        self.precision = decimal.Decimal(".%s" % ("0" * precision))
        self.rounding = rounding

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

    def to_mongo(self, value):
        value = decimal.Decimal(value)
        return str(value.quantize(self.precision, rounding=self.rounding))

    async def from_mongo(self, value, resolver=None):
        value = decimal.Decimal(value)
        return value.quantize(self.precision, rounding=self.rounding)
