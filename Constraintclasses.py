import ast


class Comparator:
    def __init__(self, op: ast.operator):
        self.operator = op


class Constraint:
    pass
    #def __init__(self, op: Optional[Comparator], left=None, right=None):
        #self.operator = op
        #lhs = left
        #rhs = right

class And(Constraint):
    def __init(self, left: Constraint, right: Constraint):
        self.lhs = left
        self.rhs = right

class Or(Constraint):
    def __init(self, left: Constraint, right: Constraint):
        self.lhs = left
        self.rhs = right

class Not(Constraint):
    def __init__(self, op: Constraint):
        self.operand = op


class Term:
    pass

class Var(Term):
    def __init__(self, name: str):
        self.name = name

class ConstStr(Term):
    def __init__(self, val: str):
        self.value = val

class ConstInt(Term):
    def __init__(self, val: int):
        self.value = val

class FunSymbol:
    pass

class CharAt(FunSymbol):
    pass

class Length(FunSymbol):
    pass

class Call(Term):
    func: FunSymbol
    args: list[Term]

class Compare(Constraint):
    def __init__(self, op: Comparator, left: Term, right: Term):
        self.operator = op
        self.lhs = left
        self.rhs = right

class Equal(Constraint): #TODO: for assigntracking
    def __init__(self, var: Var, val: Term):
        self.name = var
        self.value = val