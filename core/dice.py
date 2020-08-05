"""
Author: Mike Werezak <mwerezak@gmail.com> 
"""
#
# import math
# import random
# from numbers import Number
# from collections import Counter
# from abc import ABC, abstractmethod
# from typing import NamedTuple, Tuple, Union, Mapping, Iterable, Sequence
#
# class Bracket(NamedTuple):
#     low: float
#     high: float
#
# class CentralRandomVariable(ABC):
#     """ Mixin for random variables that have meaningful std deviation. """
#     @property
#     @abstractmethod
#     def mean(self) -> float: ...
#
#     @property
#     @abstractmethod
#     def std_dev(self) -> float: ...
#
#     @abstractmethod
#     def get_sample(self) -> Number: ...
#
#     def sigma_range(self, sigma: float) -> Bracket:
#         mean = self.mean
#         std_dev = self.std_dev
#
#         return Bracket(
#             low  = mean - sigma*std_dev,
#             high = mean + sigma*std_dev,
#         )
#
#     @property
#     def one_sigma(self) -> Bracket:
#         return self.sigma_range(1)
#     @property
#     def two_sigma(self) -> Bracket:
#         return self.sigma_range(2)
#     @property
#     def three_sigma(self) -> Bracket:
#         return self.sigma_range(3)
#
# def dice(numdice: int, sides: int = 1) -> 'DicePool':
#     """ Convenient constructor for DicePools.
#         More complex dicepools can be constructed using arithmetic operators
#         e.g. dice(3,6) + 2*dice(2,8) + 1 --> 3d6 + 4d8 + 1
#     """
#     return DicePool({sides: numdice})
#
# def dicepool(*elems: Union[int, Tuple[int, int]]) -> 'DicePool':
#     """ Takes a sequence of elements of the form: num | (num, sides)
#         and constructs a DicePool object
#         e.g. dicepool((3,6), (4,8), 1) -> 3d6 + 4d8 + 1
#     """
#     dice_counter = Counter()
#     for elem in elems:
#         if hasattr(elem, '__dicepool__'):
#             dice_counter.update(elem.__dicepool__.elements())
#         elif type(elem) is int:
#             dice_counter[1] += elem
#         else:
#             numdice, sides = elem
#             dice_counter[sides] += numdice
#     return DicePool(dice_counter)
#
# ## these are used as the built in counter math operators strip negative counts
# def _add_counter(a: Mapping[int, Number], b: Mapping[int, Number]) -> Mapping[int, Number]:
#     result = Counter()
#     for key in a.keys() | b.keys():
#         value = a.get(key, 0) + b.get(key, 0)
#         if value != 0:
#             result[key] = value
#     return result
#
# def _sub_counter(a: Mapping[int, Number], b: Mapping[int, Number]) -> Mapping[int, Number]:
#     result = Counter()
#     for key in a.keys() | b.keys():
#         value = a.get(key, 0) - b.get(key, 0)
#         if value != 0:
#             result[key] = value
#     return result
#
# class DicePool(CentralRandomVariable):
#     def __init__(self, dicepool: Union[None, 'DicePool', Mapping[int, Number]] = None):
#         ## check for the presence of a __dicepool__ magic attribute to
#         ## determine if the dicepool argument is a dicepool compatible object.
#         if not dicepool:
#             self.__dicepool__ = Counter()
#         elif hasattr(dicepool, "__dicepool__"):
#             self.__dicepool__ = Counter(dicepool.__dicepool__)
#         else:
#             self.__dicepool__ = Counter(dicepool)
#         self._remove_zeros()
#
#     def __iter__(self) -> Iterable[Tuple[int, Number]]:
#         for dicetype in sorted(self.__dicepool__, reverse=True):
#             yield (dicetype, self.__dicepool__[dicetype])
#
#     def __repr__(self) -> str:
#         # return "%s(%s)"%(type(self).__name__, repr(self.__dicepool__))
#         dice = self.__dicepool__.items() #(sides, num) tuples
#         contents = ', '.join(repr(die) for die in dice)
#         return f'{self.__class__.__name__}({contents})'
#
#     def __str__(self) -> str:
#         dice = list(self.__dicepool__.items()) #(sides, num) tuples
#         dice.sort(key=lambda pair: pair[0], reverse=True)
#
#         dicetypes = [
#             f'{num:d}d{sides:d}' if sides > 1 else f'{num:d}'
#             for sides, num in dice
#         ]
#         diceterms = ' + '.join(dicetypes) if len(dicetypes) > 0 else '0'
#         return f'[{diceterms}]'
#
#     def get_modifier(self) -> Number:
#         """ The constant part """
#         return self.__dicepool__[1]
#
#     def get_roll(self) -> Sequence[int]:
#         """ The variable part """
#         return [
#             int(math.copysign(random.randint(1, sides), numdice))
#             for sides, numdice in self.__dicepool__.items() if sides != 1
#             for i in range(abs(numdice))
#         ]
#
#     def get_roll_detailed(self) -> Mapping[int, int]:
#         """ Returns roll results organized into a dictionary """
#         return {
#             sides : [ int(math.copysign(random.randint(1, sides), numdice)) for i in range(abs(numdice)) ]
#             for sides, numdice in self.__dicepool__.items() if sides != 1
#         }
#
#     def get_roll_result(self) -> Number:
#         """ Returns roll results as a single value """
#         return sum(self.get_roll()) + self.get_modifier()
#
#     def get_sample(self) -> Number:
#         return self.get_roll_result()
#
#     ## Stats
#
#     def min(self) -> Number:
#         return sum(numdice for numdice in self.__dicepool__.values()) + self.get_modifier()
#
#     def max(self) -> Number:
#         return sum(numdice*sides for sides, numdice in self.__dicepool__.items()) + self.get_modifier()
#
#     @property
#     def mean(self) -> float:
#         return sum(
#                 numdice*(1+sides)/2
#                 for sides, numdice in self.__dicepool__.items()
#             )
#
#     @property
#     def std_dev(self) -> float:
#         return self.variance() ** 0.5
#
#     ## The variance of a sum of independent random variables is the sum of the variances.
#     def variance(self) -> float:
#         return sum(
#                 self._element_variance(sides, numdice)
#                 for sides, numdice in self.__dicepool__.items()
#             )
#
#     ## Calculates the variance of rolling a number of identical dice
#     def _element_variance(self, sides: int, num_rolls: int):
#         expected_val = (sides+1)/2
#         expected_sqr_val = sum(x*x for x in range(1, sides+1))/sides
#
#         var_oneroll = expected_sqr_val - expected_val**2
#         return num_rolls * var_oneroll
#
#     ## *** Dice Arithmetic Methods ***
#     ## For addition and subtraction other must have a __dicepool__ attribute.
#     ## e.g. dicepool((3,6), 5) + dicepool((1,6), (2,8), 2) --> dicepool((4,6), (2,8), 7)
#
#     def _remove_zeros(self):
#         for sides, numdice in list(self.__dicepool__.items()):
#             if numdice == 0:
#                 del self.__dicepool__[sides]
#
#     def __add__(self, other):
#         if isinstance(other, Number):
#             return DicePool(_add_counter(self.__dicepool__, {1: other}))
#         if hasattr(other, "__dicepool__"):
#             return DicePool(_add_counter(self.__dicepool__, other.__dicepool__))
#         return NotImplemented
#
#     def __radd__(self, other):
#         return self + other
#
#     def __sub__(self, other):
#         if isinstance(other, Number):
#             return DicePool(_sub_counter(self.__dicepool__, {1: other}))
#         if hasattr(other, "__dicepool__"):
#             return DicePool(_sub_counter(self.__dicepool__, other.__dicepool__))
#         return NotImplemented
#
#     def __rsub__(self, other):
#         if isinstance(other, Number):
#             return DicePool(_sub_counter({1: other}, self.__dicepool__))
#         if hasattr(other, "__dicepool__"):
#             return DicePool(_sub_counter(other.__dicepool__, self.__dicepool__))
#         return NotImplemented
#
#     ## multiplication and floordiv operate on ints instead of other dicepools
#     ## reverse floordiv is not supported
#     ## e.g. 5*dicepool((2,8), 3) --> dicepool((10,8), 15)
#     ## e.g. dicepool((5,8))//2 --> dicepool((2,8))
#     ## e.g. 2//dicepool(5,8) is invalid, you can't divide by a dicepool
#
#     def __mul__(self, other):
#         if isinstance(other, Number):
#             new_pool = Counter(self.__dicepool__)
#             for sides, numdice in new_pool.items():
#                 new_pool[sides] = int(numdice * other)
#             return DicePool(new_pool)
#         return NotImplemented
#
#     def __rmul__(self, other):
#         return self * other
#
#     def __floordiv__(self, other):
#         if isinstance(other, Number):
#             new_pool = Counter(self.__dicepool__)
#             for dicetype in new_pool:
#                 new_pool[dicetype] //= other
#             return DicePool(new_pool)
#         return NotImplemented
#
#     def __neg__(self):
#         new_pool = Counter(self.__dicepool__)
#         for dicetype in new_pool:
#             new_pool[dicetype] *= -1
#         return DicePool(new_pool)
#
#     ## Removes all negative or zero dice counts
#     def __abs__(self):
#         new_pool = +Counter(self.__dicepool__)
#         return DicePool(new_pool)
