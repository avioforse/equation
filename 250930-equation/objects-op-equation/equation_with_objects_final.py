class Expression:
    def substitution(self) -> "Expression":
        return self.copy()

    def copy(self) -> "Expression":
        return type(self)()

    def __eq__(self, other: "Expression") -> bool:
        return False


class Operation(Expression):
    pass


class UnaryOperation(Operation):
    def __init__(self, expr: Expression) -> None:
        super().__init__()
        self.expr = expr

    def copy(self) -> "UnaryOperation":
        return type(self)(self.expr.copy())


class Negation(UnaryOperation):
    def __str__(self) -> str:
        if isinstance(self.expr, Addition | Subtraction):
            return f"-({self.expr})"
        return f"-{self.expr}"

    def substitution(self) -> "Expression":
        if isinstance(self.expr, Value):
            return Value(-1 * self.expr.value)
        return self.copy()


class BinaryOperation(Operation):
    def __init__(self, left: Expression, right: Expression):
        super().__init__()
        self.left = left
        self.right = right

    def copy(self) -> "BinaryOperation":
        return type(self)(self.left.copy(), self.right.copy())


class Equation(BinaryOperation):
    def __str__(self) -> str:
        return f"{self.left}={self.right}"

    def standardize(self) -> "Equation":
        zero = Value(0)
        if self.right == zero:
            return self.copy()
        if self.left == zero:
            return Equation(
                left=self.right.copy(),
                right=self.left.copy(),
            )
        return Equation(
            left=Subtraction(
                left=self.left.copy(),
                right=self.right.copy(),
            ),
            right=zero,
        )

    def substitution(self) -> "Expression":
        if isinstance(self.left, Variable):
            return self.copy()
        a = self.left.substitution()
        b = self.right.copy()
        match a:
            case Negation():
                return Equation(
                    left=a.expr.copy(),
                    right=Negation(b).substitution(),
                ).substitution()
            case Addition():
                operator = Subtraction
            case Subtraction():
                operator = Addition
            case Multiplication():
                operator = Division
            case Division():
                operator = Multiplication
            case _:
                raise NotImplementedError
        if not isinstance(a.right, Value):
            raise NotImplementedError
        return Equation(
            left=a.left,
            right=operator(b, a.right).substitution(),
        ).substitution()


class Addition(BinaryOperation):
    def substitution(self) -> "Expression":
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value + right.value)
            return Addition(right, left)
        if isinstance(left, Multiplication) and isinstance(right, Multiplication):
            if (
                isinstance(left.left, Variable)
                and (right.left, Variable)
                and left.left.name == right.left.name
            ):
                return Multiplication(
                    left=left.left.copy(),
                    right=Addition(left.right.copy(), right.right.copy()),
                ).substitution()
        if not isinstance(right, Value):
            raise NotImplementedError
        return Addition(left, right)

    def __str__(self) -> str:
        return f"{self.left}+{self.right}"


class Subtraction(BinaryOperation):
    def substitution(self) -> "Expression":
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value - right.value)
            return Addition(
                left=Negation(right).substitution(),
                right=left,
            )
        if not isinstance(right, Value):
            raise NotImplementedError
        return Subtraction(left, right)

    def __str__(self) -> str:
        return f"{self.left}-{self.right}"


class Multiplication(BinaryOperation):
    def substitution(self) -> "Expression":
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value * right.value)
            return Multiplication(right, left)
        if not isinstance(right, Value):
            raise NotImplementedError
        return Multiplication(left, right)

    def __str__(self) -> str:
        left = f"{self.left}"
        if isinstance(self.left, Addition | Subtraction):
            left = f"({left})"
        right = f"{self.right}"
        if isinstance(self.right, Addition | Subtraction):
            right = f"({right})"
        return f"{left}*{right}"


class Division(BinaryOperation):
    def substitution(self) -> "Expression":
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value / right.value)
            return Multiplication(
                left=Division(Value(1), right),
                right=left,
            )
        if not isinstance(right, Value):
            raise NotImplementedError
        return Multiplication(
            left=left,
            right=Division(Value(1.0), right).substitution(),
        )

    def __str__(self) -> str:
        left = f"{self.left}"
        if isinstance(self.left, Addition | Subtraction):
            left = f"({left})"
        right = f"{self.right}"
        if isinstance(self.right, Addition | Subtraction):
            right = f"({right})"
        return f"{left}/{right}"


class Value(Expression):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    def copy(self) -> "Value":
        return type(self)(self.value)

    def __str__(self) -> str:
        if isinstance(self.value, float):
            return f"{self.value:.2f}"
        return f"{self.value}"

    def __eq__(self, other: "Expression") -> bool:
        if isinstance(other, Value) and other.value == self.value:
            return True
        return False


class Variable(Expression):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def copy(self) -> "Value":
        return type(self)(self.name)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: "Expression") -> bool:
        if isinstance(other, Variable) and other.name == self.name:
            return True
        return False


eq = Equation(
    Addition(
        Division(
            Variable("x"),
            Value(2),
        ),
        Value(7),
    ),
    Multiplication(
        Value(5),
        Value(2),
    ),
)
print(eq)

print((eq := eq.substitution()))
