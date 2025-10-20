__all__ = [
    "Value",
    "Variable",
]
from .base import Expression


class Value(Expression):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    def copy(self) -> type["Value"]:
        return type(self)(self.value)

    def __eq__(self, other: Expression) -> bool:
        return isinstance(other, Value) and other.value == self.value

    def __str__(self) -> str:
        if isinstance(self.value, float):
            return f"{self.value:.2f}"
        return f"{self.value}"


class Variable(Expression):
    def __init__(self, name: str, degree: int = 1) -> None:
        super().__init__()
        self.name = name
        self.degree = degree

    def copy(self) -> "Variable":
        return type(self)(self.name)

    def __eq__(self, other: "Expression") -> bool:
        return isinstance(other, Variable) and other.name == self.name

    def __str__(self) -> str:
        return self.name
