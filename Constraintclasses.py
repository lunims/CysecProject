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
        return f'And(lhs={self.lhs.dump()}, rhs={self.rhs.dump()})'

class Or(Constraint):
    def __init(self, left: Constraint, right: Constraint):
        self.lhs = left
        self.rhs = right

    def dump(self):
        return f'Or(lhs={self.lhs.dump()}, rhs={self.rhs.dump()})'

class Not(Constraint):
    def __init__(self, op: Constraint):
        self.operand = op

    def dump(self):
        return f'Not(op= {self.operand.dump()})'


class Term:
    def dump(self):
        pass

class Var(Term):
    def __init__(self, name: str):
        self.name = name

    def dump(self):
        return f'Var(name={self.name})'

class ConstStr(Term):
    def __init__(self, val: str):
        self.value = val

    def dump(self):
        return f'ConstStr(value={self.value})'

class ConstInt(Term):
    def __init__(self, val: int):
        self.value = val

    def dump(self):
        return f'ConstInt(value= {self.value})'
class FunSymbol:
    def dump(self):
        pass

class CharAt(FunSymbol):
    def dump(self):
        return f'charAt()'

class Length(FunSymbol):
    def dump(self):
        return f'len()'

class Call(Term):
    func: FunSymbol
    args: list[Term]
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

class Equal(Constraint): #TODO: for assigntracking
    def __init__(self, var: Var, val: Term):
        self.name = var
        self.value = val

const1 = ConstInt(val= 1)
const2 = ConstStr(val= 'a')
var = Var(name= 's')
cha = CharAt()
com = Comparator(op= ast.Eq)
call1 = Call(func= cha, args= [var, const1])
comp = Compare(op= com, left= call1, right= const2)
call2 = Call(func= Length(), args=[var, const2])
comp2 = Compare(op= com, left= call2, right=const1)
an = And(left= comp, right= comp2)
print(an.dump())