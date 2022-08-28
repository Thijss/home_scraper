from enum import Enum
from typing import Type


def convert_enum(value: str | int, enum_class: Type[Enum]):
    if isinstance(value, str):
        return enum_class[value.upper()]
    return value
