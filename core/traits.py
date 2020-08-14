from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    pass

# traits are just simple data containers that can be attached to Creatures and queried
class Trait:
    name: str
    key: Any
    desc: str = ''

    def __init__(self, **data):
        for name, value in data.items():
            super().__setattr__(name, value)

    def __setattr__(self, name, value):
        raise TypeError

    @property
    def key(self) -> Any:
        return type(self)

    def __repr__(self) -> str:
        ignore = ['name', 'key']
        data = ', '.join(
            f'{k}={v!r}' for k,v in self.__dict__.items() if k not in ignore
        )
        return f'{self.__class__.__name__}({data})'

