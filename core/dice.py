from __future__ import annotations

import math
import random
from collections import Counter
from numbers import Number
from typing import TYPE_CHECKING, Any, Tuple, Union, Mapping, Iterable, Sequence, Counter as CounterType

if TYPE_CHECKING:
    pass

def dice(numdice: int, sides: int = 1) -> DicePool:
    """ Convenient constructor for DicePools.
        More complex dicepools can be constructed using arithmetic operators
        e.g. dice(3,6) + 2*dice(2,8) + 1 --> 3d6 + 4d8 + 1
    """
    return DicePool({sides: numdice})

def dicepool(*elems: Union[Number, Tuple[int, int]]) -> DicePool:
    """ Takes a sequence of elements of the form: num | (num, sides)
        and constructs a DicePool object
        e.g. dicepool((3,6), (4,8), 1) -> 3d6 + 4d8 + 1
    """
    dice_counter = Counter()
    for elem in elems:
        if hasattr(elem, '__dicepool__'):
            dice_counter.update(elem.__dicepool__.elements())
        elif type(elem) is int:
            dice_counter[1] += elem
        else:
            numdice, sides = elem
            dice_counter[sides] += numdice
    return DicePool(dice_counter)

class DicePool:
    __dicepool__: CounterType[int, Number]

    def __init__(self, pool = None):
        ## check for the presence of a __dicepool__ magic attribute to
        ## determine if the dicepool argument is a dicepool compatible object.
        if not pool:
            self.__dicepool__ = Counter()
        elif hasattr(pool, "__dicepool__"):
            self.__dicepool__ = Counter(pool.__dicepool__)
        else:
            self.__dicepool__ = Counter(pool)
        self.__remove_zeros()

    def __iter__(self) -> Iterable[Tuple[int, Number]]:
        for dicetype, numdice in sorted(self.__dicepool__.items(), reverse=True):
            yield dicetype, numdice

    def __repr__(self) -> str:
        contents = ', '.join(repr(die) for die in self)
        return f'{self.__class__.__name__}({contents})'

    def __str__(self) -> str:
        parts = []
        for i, item in enumerate(sorted(self, key=lambda pair: pair[0], reverse=True)):
            sides, numdice = item
            if i > 0:
                parts.append(' + ' if numdice >= 0 else ' - ')
                numdice = abs(numdice)
            parts.append(f'{numdice:d}d{sides:d}' if sides != 1 else f'{numdice}')
        return ''.join(parts) if len(parts) > 0 else '0'

    def get_modifier(self) -> Any:
        """ The constant part """
        return self.__dicepool__[1]

    def get_roll(self) -> Iterable[int]:
        """ The variable part """
        return (
            int(math.copysign(random.randint(1, sides), numdice))
            for sides, numdice in self.__dicepool__.items() if sides != 1
            for _ in range(abs(numdice))
        )

    def get_roll_detailed(self) -> Mapping[int, Sequence[int]]:
        """ Returns roll results organized into a dictionary """
        return {
            sides : [ int(math.copysign(random.randint(1, sides), numdice)) for _ in range(abs(numdice)) ]
            for sides, numdice in self.__dicepool__.items() if sides != 1
        }

    def get_roll_result(self) -> Number:
        """ Returns roll results as a single value """
        return sum(self.get_roll()) + self.get_modifier()

    ## Stats

    def min(self) -> Number:
        return sum(
            numdice if numdice > 0 else numdice*sides
            for sides, numdice in self.__dicepool__.items()
        )

    def max(self) -> Number:
        return sum(
            numdice*sides if numdice > 0 else numdice
            for sides, numdice in self.__dicepool__.items()
        )

    def mean(self) -> float:
        return sum(
                numdice*(1+sides)/2
                for sides, numdice in self.__dicepool__.items()
            )

    def std_dev(self) -> float:
        return self.variance() ** 0.5

    ## The variance of a sum of independent random variables is the sum of the variances.
    def variance(self) -> float:
        return sum(
                self.__element_variance(sides, numdice)
                for sides, numdice in self.__dicepool__.items()
            )

    ## Calculates the variance of rolling a number of identical dice
    @staticmethod
    def __element_variance(sides: int, num_rolls: int) -> float:
        expected_val = (sides+1)/2
        expected_sqr_val = sum(x*x for x in range(1, sides+1))/sides

        var_oneroll = expected_sqr_val - expected_val**2
        return num_rolls * var_oneroll

    ## *** Dice Arithmetic Methods ***
    ## For addition and subtraction other must have a __dicepool__ attribute.
    ## e.g. dicepool((3,6), 5) + dicepool((1,6), (2,8), 2) --> dicepool((4,6), (2,8), 7)

    def __remove_zeros(self) -> None:
        for sides, numdice in list(self.__dicepool__.items()):
            if numdice == 0:
                del self.__dicepool__[sides]

    ## these are used as the built in counter math operators strip negative counts
    @staticmethod
    def __add_counter(a: Mapping[int, Number], b: Mapping[int, Number]) -> Mapping[int, Number]:
        result = Counter()
        for key in a.keys() | b.keys():
            value = a.get(key, 0) + b.get(key, 0)
            if value != 0:
                result[key] = value
        return result

    @staticmethod
    def __sub_counter(a: Mapping[int, Number], b: Mapping[int, Number]) -> Mapping[int, Number]:
        result = Counter()
        for key in a.keys() | b.keys():
            value = a.get(key, 0) - b.get(key, 0)
            if value != 0:
                result[key] = value
        return result

    def __add__(self, other) -> DicePool:
        if isinstance(other, Number):
            return DicePool(self.__add_counter(self.__dicepool__, {1: other}))
        if hasattr(other, "__dicepool__"):
            return DicePool(self.__add_counter(self.__dicepool__, other.__dicepool__))
        return NotImplemented

    def __radd__(self, other) -> DicePool:
        return self + other

    def __sub__(self, other) -> DicePool:
        if isinstance(other, Number):
            return DicePool(self.__sub_counter(self.__dicepool__, {1: other}))
        if hasattr(other, "__dicepool__"):
            return DicePool(self.__sub_counter(self.__dicepool__, other.__dicepool__))
        return NotImplemented

    def __rsub__(self, other) -> DicePool:
        if isinstance(other, Number):
            return DicePool(self.__sub_counter({1: other}, self.__dicepool__))
        if hasattr(other, "__dicepool__"):
            return DicePool(self.__sub_counter(other.__dicepool__, self.__dicepool__))
        return NotImplemented

    ## multiplication and floordiv operate on ints instead of other dicepools
    ## reverse floordiv is not supported
    ## e.g. 5*dicepool((2,8), 3) --> dicepool((10,8), 15)
    ## e.g. dicepool((5,8))//2 --> dicepool((2,8))
    ## e.g. 2//dicepool(5,8) is invalid, you can't divide by a dicepool

    def __mul__(self, other) -> DicePool:
        if isinstance(other, Number):
            new_pool = Counter(self.__dicepool__)
            for sides, numdice in new_pool.items():
                new_pool[sides] = round(numdice * other) if sides != 1 else numdice * other
            return DicePool(new_pool)
        return NotImplemented

    def __rmul__(self, other) -> DicePool:
        return self * other

    def __truediv__(self, other) -> DicePool:
        if isinstance(other, Number):
            new_pool = Counter(self.__dicepool__)
            for sides, numdice in new_pool.items():
                new_pool[sides] = round(numdice / other) if sides != 1 else numdice / other
            return DicePool(new_pool)
        return NotImplemented

    def __floordiv__(self, other) -> DicePool:
        if isinstance(other, Number):
            new_pool = Counter(self.__dicepool__)
            for sides, numdice in new_pool.items():
                new_pool[sides] = int(numdice // other)
            return DicePool(new_pool)
        return NotImplemented

    def __neg__(self) -> DicePool:
        new_pool = Counter(self.__dicepool__)
        for dicetype in new_pool:
            new_pool[dicetype] *= -1
        return DicePool(new_pool)

    ## Removes all negative or zero dice counts
    def __abs__(self) -> DicePool:
        new_pool = +Counter(self.__dicepool__)
        return DicePool(new_pool)
