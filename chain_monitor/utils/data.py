from easydict import EasyDict


def easy_dictify(d):
    """ Recursive make EasyDict """

    if isinstance(d, dict):
        new_data = {}
        for key, value in d.items():
            value = easy_dictify(value)
            new_data[key] = value
        return EasyDict(new_data)
    elif isinstance(d, (list, tuple)):
        return [easy_dictify(x) for x in d]

    return d


class SimpleEnumMetaclass(type):
    """
    Simpler alternative to Enum, when we want to just deal with strings

    This adds the ability to check membership and to iterate
    """

    def __init__(cls, name, bases, attrs):
        values = []

        for key, val in attrs.items():
            if not key.startswith('_') and isinstance(val, str):
                values.append(val)

        super(SimpleEnumMetaclass, cls).__init__(name, bases, attrs)
        cls._values = tuple(values)
        cls._values_set = set(values)

    def __iter__(cls):
        return iter(cls._values)

    def __contains__(cls, value):
        return value in cls._values_set


class SimpleEnum(metaclass=SimpleEnumMetaclass):
    pass
