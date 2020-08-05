from functools import total_ordering
from typing import overload

class IntClassMeta(type):
    def __call__(cls, value: int):
        cache_name = f'__{cls.__name__}_cache_'
        cache = getattr(cls, cache_name, None)
        if cache is None:
            cache = {}
            setattr(cls, cache_name, cache)
        instance = cache.get(value, None)
        if instance is None:
            instance = super().__call__(value)
            # if instance.value differs from value, create an alias and discard instance
            cache[value] = cache.get(instance.value, instance)
        return instance

@total_ordering
class IntClass(metaclass=IntClassMeta):
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
