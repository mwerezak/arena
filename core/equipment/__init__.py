from typing import Protocol

class Equipment(Protocol):
    name: str
    cost: int

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'