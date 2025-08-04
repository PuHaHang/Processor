

from enum import Enum


class Platform(Enum):
    """
    플랫폼 타입
    """

    def __new__(cls, value: str, index: int):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.index = index
        return obj

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def from_value(cls, value: str) -> "Platform":
        for member in cls:
            if member.value.upper() == value.upper():
                return member
        return cls.UNKNOWN
    
    @classmethod
    def from_index(cls, index: int) -> "Platform":
        for member in cls:
            if member.index == index:
                return member
        return cls.UNKNOWN


    UNKNOWN = ("UNKNOWN", 0)
    YOUTUBE = ("YOUTUBE", 1)
    INSTAGRAM = ("INSTAGRAM", 2)
    