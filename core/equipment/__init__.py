from typing import Protocol

class Equipment(Protocol):
    name: str
    cost: float

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'