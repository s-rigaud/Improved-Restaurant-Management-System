class ScientCalc:
    def __init__(self):
        # Strategic order (scientific calculus + negative number)
        self._operands = ["+", "-", "/", "*"]

    def compute_string(self, calculator_str: str):
        if calculator_str:
            res, error = self._compute(part1=calculator_str)
            res = round(res, 2)
            if res == int(res):
                res = int(res)
            return (res, error)
        return (0, False)

    def _compute(self, operand: str = "+", part1: str = "0", part2: str = "0") -> float:
        """Recursive function trying to divide operations and compute (Tree style)"""
        error = False
        try:
            res1 = float(part1)
        except ValueError:
            for o in self._operands:
                split_str = part1.rsplit(o, 1)
                if len(split_str) > 1:
                    res1, err = self._compute(o, split_str[0], split_str[1])
                    error |= err
                    break
        try:
            res2 = float(part2)
        except ValueError:
            for o in self._operands:
                split_str = part2.rsplit(o, 1)
                if len(split_str) > 1:
                    res2, err = self._compute(o, split_str[0], split_str[1])
                    error |= err
                    break

        operand_dict = {"+": self._add, "-": self._sub, "*": self._mul, "/": self._div}
        try:
            return (operand_dict[operand](res1, res2), error)
        except (UnboundLocalError, ZeroDivisionError):
            error = True
            return (0, error)

    def _add(self, f1: float, f2: float) -> float:
        """Simple adder"""
        return f1 + f2

    def _sub(self, f1: float, f2: float) -> float:
        """Simple substracter"""
        return f1 - f2

    def _mul(self, f1: float, f2: float) -> float:
        """Simple product"""
        return f1 * f2

    def _div(self, f1: float, f2: float) -> float:
        """Simple div.."""
        return f1 / f2
