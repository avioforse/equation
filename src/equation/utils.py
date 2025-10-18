__all__ = [
    "solution_of_equation",
    "tokenize",
    "tokens_in_equation",
]

from .operators import (
    Addition,
    Brackets,
    Division,
    Equation,
    Multiplication,
    Negation,
    Subtraction,
)
from .units import Value, Variable

_Tokens = list[str | float]


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
                Brackets(tokens_in_equation(tokens[index_l + 1 : index_r])),
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
                                        expr=tokens_in_equation(tokens[index + 1]),
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


def tokenize(user_input: str) -> _Tokens:
    tokens = []
    for index, value in enumerate(user_input):
        if (value).isdigit():
            tokens.append(value)
            if index != 0 and (tokens[-2]).isdigit():
                tokens[-2] += tokens[-1]
                tokens.pop(-1)
        else:
            tokens.append(value)
    for index, value in enumerate(tokens):
        if value == ".":
            tokens[index - 1] = float(
                tokens[index - 1] + value + tokens[index + 1],
            )
            tokens.pop(index + 1), tokens.pop(index)
    return tokens


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
