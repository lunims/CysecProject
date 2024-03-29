import ast


class Comparator:
    def __init__(self, op: ast.operator):
        self.operator = op

    def dump(self):
        return f'{self.operator}'


class Constraint:
    def dump(self):
        pass

class And(Constraint):
    def __init__(self, left: Constraint, right: Constraint):
        self.lhs = left
        self.rhs = right

    def dump(self):
        return 'And{' + f'lhs={self.lhs.dump()}, rhs={self.rhs.dump()}' + '}'

class Or(Constraint):
    def __init__(self, left: Constraint, right: Constraint):
        self.lhs = left
        self.rhs = right

    def dump(self):
        return 'Or{' + f'lhs={self.lhs.dump()}, rhs={self.rhs.dump()}' + '}'

class Not(Constraint):
    def __init__(self, op: Constraint):
        self.operand = op

    def dump(self):
        return f'Not(op={self.operand.dump()})'


class Term:
    def dump(self):
        pass

class Var(Term):
    def __init__(self, name: str):
        self.name = name

    def dump(self):
        return f'Var(name={self.name})'

class ConstBool(Term):
    def __init__(self, val: bool):
        self.value = val
    def dump(self):
        return f'ConstBool(value={self.value})'

class ConstStr(Term):
    def __init__(self, val: str):
        self.value = val

    def dump(self):
        return f'ConstStr(value={self.value})'

class ConstInt(Term):
    def __init__(self, val: int):
        self.value = val

    def dump(self):
        return f'ConstInt(value={self.value})'
class FunSymbol:
    def __init__(self):
        pass
    def dump(self):
        pass

class startsWith(FunSymbol):
    def dump(selfs):
        return f'startsWith()'

class CharAt(FunSymbol):
    def dump(self):
        return f'charAt()'

class Length(FunSymbol):
    def dump(self):
        return f'len()'

class EndsWith(FunSymbol):
    def dump(self):
        return f'endsWith()'

class Contains(FunSymbol):
    def dump(self):
        return f'contains()'

class Call(Term):
    def __init__(self, func: FunSymbol, args: list[Term]):
        self.func = func
        self.args = args

    def dump(self):
        res = ''
        for arg in self.args:
            res += arg.dump()
        return f'Call(func={self.func.dump()}, args=[{res}])'


class Compare(Constraint):
    def __init__(self, op: Comparator, left: Term, right: Term):
        self.operator = op
        self.lhs = left
        self.rhs = right

    def dump(self):
        return f'Compare(operator={self.operator.dump()}, lhs={self.lhs.dump()}, rhs={self.rhs.dump()})'

class Equal(Constraint):
    def __init__(self, var: Var, val: Term):
        self.name = var
        self.value = val

    def dump(self):
        return f'Equal(name={self.name.dump()}, value={self.value.dump()})'
