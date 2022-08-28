from enum import IntEnum


class Status(IntEnum):
    UNKNOWN = 0
    AVAILABLE = 1
    VIEWING = 2
    RENTED = 3
    OLD = 4
