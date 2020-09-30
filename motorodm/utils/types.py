import types

_CALLABLE_TYPES = (
    types.FunctionType,
    types.BuiltinFunctionType,
    types.MethodType,
    types.BuiltinMethodType,
    types.LambdaType
)


def is_callable(value):
    return isinstance(value, _CALLABLE_TYPES)
