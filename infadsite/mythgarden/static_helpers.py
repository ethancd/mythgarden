from collections.abc import Iterable


def guard_types(lst, cls):
    """Returns True if all objects in lst are instances of cls, else raises a TypeError"""
    for obj in lst:
        guard_type(obj, cls)
    return True


def guard_type(obj, cls):
    """Returns True if obj is an instance of cls, else raises a TypeError"""
    if isinstance(obj, cls):
        return True
    else:
        raise TypeError(f"{obj} is not a valid {cls} object")


def srs_serialize(obj):
    if isinstance(obj, Iterable):
        return [srs_serialize(i) for i in obj]
    else:
        return obj.serialize()
