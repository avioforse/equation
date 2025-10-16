class Expression:
    pass


class Variable(Expression):
    def __init__(self, mean, cir=1, ng=1):
        self.mean = mean
        self.cir = cir
        self.ng = ng


class Equality(Expression):
    pass


class Operator(Expression):
    pass


class UnaryOperator(Operator):
    def __init__(self, right):
        super().__init__()
        self.right = right


class BinaryOperator(Operator):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    def simpl(self):
        if isinstance(self.left, int) and isinstance(self.right, int):
            return self.action()


class Multiplication(BinaryOperator):
    def action(self):
        if isinstance(self.left, int) and isinstance(self.right, int):
            return self.left * self.right

    def standart(self):
        if isinstance(self.left, Variable):
            return Multiplication(left=self.left, right=self.right)
        if isinstance(self.right, Variable):
            return Multiplication(left=self.right, right=self.left)
        else:
            return Multiplication(left=self.left, right=self.right)


class Division(BinaryOperator):
    def action(self):
        if isinstance(self.left, int) and isinstance(self.right, int):
            return self.left / self.right

    def standart(self):
        if isinstance(self.left, Variable):
            return Division(left=self.left, right=self.right)
        if isinstance(self.right, Variable):
            return Multiplication(left=self.right, right=self.left)
        else:
            return Division(left=self.left, right=self.right)


class Addition(BinaryOperator):
    def action(self):
        if isinstance(self.left, int) and isinstance(self.right, int):
            return self.left + self.right
        else:
            pass

    def standart(self):
        if isinstance(self.left, Variable):
            return Addition(left=self.left, right=self.right)
        if isinstance(self.right, Variable):
            return Addition(left=self.right, right=self.left)
        else:
            return Addition(left=self.left, right=self.right)


class Subtraction(BinaryOperator):
    def action(self):
        if isinstance(self.left, int) and isinstance(self.right, int):
            return self.left - self.right

    def standart(self):
        if isinstance(self.left, Variable):
            return Subtraction(left=self.left, right=self.right)
        if isinstance(self.right, Variable):
            return Addition(left=self.right, right=self.left)
        else:
            return Subtraction(left=self.left, right=self.right)


class Negation(UnaryOperator):
    pass


_Token = int | str | Expression


def tokenize(string: str) -> list[_Token]:
    tokens = []
    for a in string:
        if a.isdigit():
            tokens.append(int(a))
            if string.index(a) != 0 and isinstance(tokens[-2], int):
                tokens[-2] = tokens[-1] + tokens[-2] * 10
                tokens.pop(-1)
        else:
            tokens.append(a)
    return tokens


def tokens_standartize(tokens: list[_Token]) -> list[_Token]:
    """Assigning data types."""
    adt = []
    for i, ch in enumerate(tokens):
        match ch:
            case "x":
                ch = Variable(tokens[i])
            case "*" | Multiplication():
                ch = Multiplication(tokens[i - 1], tokens[i + 1])
            case "+" | Addition():
                ch = Addition(tokens[i - 1], tokens[i + 1])
            case "-" | Subtraction():
                ch = Subtraction(tokens[i - 1], tokens[i + 1])
            case "/" | Division():
                ch = Division(tokens[i - 1], tokens[i + 1])
            case "=":
                ch = Equality()
            case _:
                pass
        adt.append(ch)
        if isinstance(ch, Subtraction) and len(adt) == 1:
            ch = Negation(tokens[i + 1])
            adt.pop(-1)
            adt.append(ch)
        if (
            len(adt) >= 2
            and isinstance(ch, Subtraction)
            and isinstance(adt[-2], Equality)
        ):
            ch = Negation(tokens[i + 1])
            adt.pop(-1)
            adt.append(ch)
    return adt


tokens = tokenize(input("Введите выражение:"))
tokens = tokens_standartize(tokens)

while len(tokens) > 3:
    tokens = tokens_standartize(tokens)

    for ch in tokens:
        i = tokens.index(ch)
        if isinstance(ch, UnaryOperator):
            tokens[i + 1] = tokens[i + 1] * (-1)
            tokens.pop(i)
            break

        if isinstance(ch, BinaryOperator):
            if isinstance(tokens[i + 1], Variable):
                match ch:
                    case Addition() | Multiplication():
                        ch = ch.standart()
                        tokens[i - 1] = ch.left
                        tokens[i + 1] = ch.right
                    case Subtraction():
                        ch = ch.standart()
                        tokens[i - 1] = ch.left
                        tokens[i + 1] = ch.right
                        tokens[i - 1].ng = -1
                    case Division():
                        ch = ch.standart()
                        tokens[i - 1] = ch.left
                        tokens[i + 1] = ch.right
                        tokens[i - 1].cir = -1

            if isinstance(ch.simpl(), (int, float)):
                tokens[i] = ch.simpl()
                tokens.pop(i + 1)
                tokens.pop(i - 1)
                break
            else:
                match ch:
                    case Subtraction():
                        a = "+"
                    case Addition():
                        a = "-"
                    case Multiplication():
                        a = "/"
                    case Division():
                        a = "*"
                    case _:
                        pass
                tokens.append(a)
                tokens.append(ch.right)
                tokens.pop(i + 1)
                tokens.pop(i)
if len(tokens) == 3:
    for i in tokens:
        if isinstance(i, (int, float)):
            A = i
        if isinstance(i, Variable):
            cir = i.cir
            ng = i.ng
    answer = (A * ng) ** cir

print("Ответ: x =", answer)
