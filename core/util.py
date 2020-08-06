
class IntClass(int):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self:d})'

    def get_step(self, step: int) -> 'IntClass':
        return self.__class__(self + step)