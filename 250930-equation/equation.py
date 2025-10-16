_Tokens = list[str | float]


class Expression:
    def copy(self) -> "Expression":
        return type(self)()

    def __eq__(self, other: "Expression") -> bool:
        return False

    def substitution(self) -> "Expression":
        return self.copy()


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
        if isinstance(self.expr, Addition | Subtraction):
            return type(self.expr)(
                left=Negation(self.expr.left).substitution(),
                right=Negation(self.expr.right).substitution(),
            ).substitution()
        if isinstance(self.expr, Negation):
            return self.expr.expr
        return self.copy()


class BinaryOperator(Operation):
    def __init__(self, left: Expression, right: Expression):
        super().__init__()
        self.left = left
        self.right = right

    def copy(self) -> "BinaryOperator":
        return type(self)(self.left.copy(), self.right.copy())


class Equation(BinaryOperator):
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
        if isinstance(self.left, Negation) and isinstance(self.right, Negation):
            return Equation(left=self.left.expr, right=self.right.expr).substitution()
        if isinstance(self.left, Variable):
            if isinstance(self.right, Value):
                return self
        a = self.left.substitution()
        b = self.right.copy().substitution()
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
            case Brackets():
                a = a.expr
                if isinstance(a, Addition):
                    operator = Subtraction
                if isinstance(a, Subtraction):
                    operator = Addition
            case Variable():
                print(Equation(a, b))
                return Equation(left=a, right=b)
            case _:
                raise NotImplementedError
        return Equation(
            left=a.left,
            right=operator(b, a.right).substitution(),
        ).substitution()


class Addition(BinaryOperator):
    def __str__(self) -> str:
        return f"{self.left}+{self.right}"

    def substitution(self) -> "Expression":
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value + right.value)
            return Addition(right, left)
        if right == Value(0):
            return left
        if isinstance(left, Multiplication) and isinstance(left.left, Variable):
            if isinstance(right, Multiplication) and isinstance(right.left, Variable):
                return Multiplication(
                    left=left.left,
                    right=Addition(left=left.right, right=right.right).substitution(),
                ).substitution()
            if isinstance(right, Variable):
                return Multiplication(
                    left=left.left,
                    right=Addition(left=left.right, right=Value(1)),
                )
        if isinstance(left, Variable):
            if isinstance(right, Multiplication) and isinstance(right.left, Variable):
                return Multiplication(
                    left=left,
                    right=Addition(left=Value(1), right=right.right).substitution(),
                ).substitution()
        if (
            isinstance(left, Addition | Subtraction)
            and isinstance(left.right, Value)
            and not isinstance(right, Value)
        ):
            return type(left)(
                left=Addition(left=left.left, right=right).substitution(),
                right=left.right,
            ).substitution()
        return Addition(left, right)


class Subtraction(BinaryOperator):
    def __str__(self) -> str:
        return f"{self.left}-{self.right}"

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
        if isinstance(left, Multiplication) and isinstance(left.left, Variable):
            if isinstance(right, Multiplication) and isinstance(right.left, Variable):
                return Multiplication(
                    left=left.left,
                    right=Subtraction(
                        left=left.right, right=right.right
                    ).substitution(),
                ).substitution()
            if isinstance(right, Variable):
                return Multiplication(
                    left=left.left,
                    right=Subtraction(left=left.right, right=Value(1)),
                )
        if isinstance(left, Variable):
            if isinstance(right, Multiplication) and isinstance(right.left, Variable):
                return Multiplication(
                    left=left,
                    right=Subtraction(left=Value(1), right=right.right).substitution(),
                ).substitution()
        if (
            isinstance(left, Addition | Subtraction)
            and isinstance(left.right, Value)
            and not isinstance(right, Value)
        ):
            return type(left)(
                left=Subtraction(left=left.left, right=right).substitution(),
                right=left.right,
            ).substitution()
        return Subtraction(left, right)


class Multiplication(BinaryOperator):
    def __str__(self) -> str:
        left = f"{self.left}"
        if isinstance(self.left, Addition | Subtraction):
            left = f"({left})"
        right = f"{self.right}"
        if isinstance(self.right, Addition | Subtraction):
            right = f"({right})"
        return f"{left}*{right}"

    def substitution(self) -> "Expression":
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value * right.value)
            if isinstance(right, Brackets):
                right = right.expr.copy().substitution()
                left_b = right.left
                right_b = right.right
                return type(right)(
                    left=Multiplication(left, left_b),
                    right=Multiplication(left, right_b),
                )
            return Multiplication(right, left).substitution()
        if isinstance(left, Multiplication):
            if isinstance(right, Value):
                return Multiplication(
                    left=left.left,
                    right=Multiplication(left=left.right, right=right).substitution(),
                )
        if isinstance(left, Addition | Subtraction):
            return type(left)(
                left=Multiplication(left.left, right).substitution(),
                right=Multiplication(left.right, right).substitution(),
            ).substitution()
        return Multiplication(left, right)


class Division(BinaryOperator):
    def __str__(self) -> str:
        left = f"{self.left}"
        if isinstance(self.left, Addition | Subtraction):
            left = f"({left})"
        right = f"{self.right}"
        if isinstance(self.right, Addition | Subtraction):
            right = f"({right})"
        return f"{left}/{right}"

    def substitution(self) -> "Expression":
        if (
            isinstance(self.left, Value)
            and self.left.value == 1
            and isinstance(self.right, Variable)
        ):
            return Variable(self.right.name, degree=-1)
        left = self.left.copy().substitution()
        right = self.right.copy().substitution()
        if isinstance(left, Value):
            if isinstance(right, Value):
                return Value(left.value / right.value)
            if isinstance(right, Brackets):
                right = right.expr.copy().substitution()
                left_b = right.left
                right_b = right.right
                return type(right)(
                    left=Division(left, left_b), right=Division(left, right_b)
                )
            return Multiplication(
                left=Division(Value(1), right),
                right=left,
            )
        if isinstance(left, Addition | Subtraction) and isinstance(right, Value):
            return type(left)(
                left=Division(left=left.left, right=right),
                right=Division(left=left.right, right=right),
            )
        return Multiplication(
            left=left,
            right=Division(Value(1.0), right).substitution(),
        )


class Value(Expression):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    def copy(self):
        return type(self)(self.value)

    def __eq__(self, other: Expression) -> bool:
        if isinstance(other, Value) and other.value == self.value:
            return True
        return False

    def __str__(self) -> str:
        if isinstance(self.value, float):
            return f"{self.value:.2f}"
        return f"{self.value}"


class Variable(Expression):
    def __init__(self, name: str, degree=1) -> None:
        super().__init__()
        self.name = name
        self.degree = degree

    def copy(self) -> "Variable":
        return type(self)(self.name)

    def __eq__(self, other: "Expression") -> bool:
        if isinstance(other, Variable) and other.name == self.name:
            return True
        return False

    def __str__(self) -> str:
        return self.name


class Brackets(UnaryOperation):
    def __init__(self, expr):
        super().__init__(expr)

    def __str__(self) -> str:
        return f"({self.expr})"

    def substitution(self) -> "Expression":
        return self.expr.copy()


def tokenize(user_input: str) -> _Tokens:
    tokens = []
    for index, value in enumerate(user_input):
        if (value).isdigit():
            tokens.append(value)
            if index != 0 and (tokens[-2]).isdigit():
                tokens[-2] += tokens[-1]
                tokens.pop(-1)
        else:
            tokens.append(user_input[index])
    for index, value in enumerate(tokens):
        if value == ".":
            tokens[index - 1] = float(
                tokens[index - 1] + tokens[index] + tokens[index + 1]
            )
            tokens.pop(index + 1), tokens.pop(index)
    return tokens


def tokens_in_equation(tokens: _Tokens) -> Equation:
    print(tokens)
    try:
        index = tokens.index("=")
        operator = Equation
    except ValueError:
        try:
            index_l = tokens.index("(")
            index_r = tokens.index(")")
            tokens[index_l : index_r + 1] = [
                Brackets(tokens_in_equation(tokens[index_l + 1 : index_r]))
            ]
            return tokens_in_equation(tokens)
        except ValueError:
            try:
                index = tokens.index("+")
                operator = Addition
            except ValueError:
                try:
                    index = tokens.index("-")
                    if index != 0:
                        operator = Subtraction
                    else:
                        index = tokens.index("-", index + 1)
                        operator = Subtraction
                except ValueError:
                    try:
                        index = tokens.index("*")
                        operator = Multiplication
                    except ValueError:
                        try:
                            index = tokens.index("/")
                            operator = Division
                        except ValueError:
                            try:
                                index = tokens.index("-")
                                if index == 0:
                                    return Negation(
                                        expr=tokens_in_equation(tokens[index + 1])
                                    )
                            except ValueError:
                                try:
                                    index = tokens.index("x")
                                    return Variable(tokens[0])
                                except ValueError:
                                    try:
                                        return Value(float(tokens))
                                    except TypeError:
                                        try:
                                            return Value(float(tokens[0]))
                                        except TypeError:
                                            return tokens[0]
    return operator(
        left=tokens_in_equation(tokens[:index]),
        right=tokens_in_equation(tokens[index + 1 :]),
    )


def solution_of_equation(user_input: str) -> float:
    tokens = tokenize(user_input)
    equation = tokens_in_equation(tokens)
    standart_equation = equation.standardize()
    answer = standart_equation.substitution()
    while True:
        if not isinstance(answer.right, Value):
            answer_check = answer.substitution()
            if print(answer_check) == print(answer):
                answer = Equation(
                    left=Subtraction(left=answer.right, right=answer.left),
                    right=Value(0),
                ).substitution()
                continue
        break
    return float(f"{(answer.right.value) ** answer.left.degree:.2f}")
