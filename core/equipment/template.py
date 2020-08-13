
class EquipmentTemplate:
    name: str
    cost: int
    encumbrance: float = 0.0

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name!r}>'
