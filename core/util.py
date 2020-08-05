from functools import total_ordering
from typing import overload

@total_ordering
class IntClass:
    def __init__(self, value: int):
        self.__value = value

    @property
    def value(self) -> int:
        return self.__value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value:d})'

    def __add__(self, other: int) -> 'IntClass':  # increment
        return self.__class__(self.value + other)

    @overload
    def __sub__(self, other: int) -> 'IntClass':  # decrement
        ...
    @overload
    def __sub__(self, other: 'IntClass') -> int:  # distance between two IntClass values
        ...
    def __sub__(self, other):
        if isinstance(other, IntClass):
            return self.value - other.value
        return self.__class__(self.value - other)

    def __lt__(self, other: 'IntClass') -> bool:
        return self.value < other.value
    def __eq__(self, other: 'IntClass') -> bool:
        return self.value == other.value
