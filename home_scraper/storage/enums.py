from enum import IntEnum


class StorageMode(IntEnum):
    LOCAL = 1
    AWS_LOCAL = 2
    AWS_LAMBDA = 3
