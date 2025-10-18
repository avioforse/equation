class Expression:
    def copy(self) -> "Expression":
        return type(self)()

    def __eq__(self, other: "Expression") -> bool:
        return False

    def substitution(self) -> "Expression":
        return self.copy()
