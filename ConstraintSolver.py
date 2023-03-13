#import isla
#from isla.solver import ISLaSolver
import re
import Constraintclasses
from Constraintclasses import *
import ast
from TypeInferer import TypeInferer


class ConstraintSolver:

    def entrace(self, constraint: Constraint):
        res = self.visitConstraint(constraint)
        return res

    def visitConstraint(self, constraint: Constraint):
        if isinstance(constraint, And):
            return self.visitAnd(constraint)
        elif isinstance(constraint, Or):
            return self.visitOr(constraint)
        elif isinstance(constraint, Not):
            return self.visitNot(constraint)
        elif isinstance(constraint, Equal):
            return self.visitEqual(constraint)
        elif isinstance(constraint, Compare):
            return self.visitCompare(constraint)
        else:
            raise Exception

    def visitAnd(self, a: And):
        return f'^(?=.{self.visitConstraint(a.lhs)})(?=.{self.visitConstraint(a.rhs)}).*$'

    def visitOr(self, o: Or):
        return self.visitConstraint(o.lhs) + '|' + self.visitConstraint(o.rhs)

    def visitNot(self, no: Not):
        return '[^' + self.visitConstraint(no.operand) + ']*$'

    #TODO vor visit über Constraint gehen und unseren String namen auf die linke seite schieben
    def visitCompare(self, comp: Compare):
        if isinstance(comp.lhs, Call):
            if comp.lhs.func is Constraintclasses.CharAt:
                return self.evalCharAt(comp.lhs, comp.rhs, comp.operator)
            elif comp.lhs.func is Length:
                return self.evalLen(comp.rhs, comp.operator)
            else:
                raise NotImplementedError
        elif isinstance(comp.lhs, Var):
            match comp.op:
                case ast.Eq:
                    return self.evalEquals(comp.rhs)
                case ast.NotEq:
                    return self.evalNotEquals(comp.rhs)
                case _:
                    raise NotImplementedError

    def visitEqual(self, equal: Equal):
        pass

    def evalCharAt(self, lhs: Call, rhs: ConstStr, op: Comparator):
        match op.operator:
            case ast.Eq():
                x = lhs.args[1].value
                h ='^'
                for i in range(x-1):
                    h += '.'
                h += rhs.value
                return h
            case ast.NotEq():
                x = lhs.args[1]
                h = '^'
                for i in range(x - 1):
                    h += '.'
                h += rhs.value
                return h
            case _:
                raise NotImplementedError


    def evalLen(self, rhs: ConstInt, op: Comparator):
        match op.operator:
            case ast.Eq():
                return '{' + str(rhs.value) + '}'
            case ast.NotEq():
                return '{,' + str(rhs.value-1) + '}{' + str(rhs.value+1) + ',}'
            case ast.Lt():
                return '{0,' + str(rhs.value-1) + '}'
            case ast.LtE():
                return '{0,' + str(rhs.value) + '}'
            case ast.Gt():
                return '{' + str(rhs.value+1) + ',}'
            case ast.GtE():
                return '{' + str(rhs.value) + ',}'
            case _:
                raise NotImplementedError

    def evalEquals(self, rhs: ConstStr):
        return rhs.value

    def evalNotEquals(self, rhs: ConstStr):
        return f'^(?!{rhs.value}$).*$'

    def visitConstStr(self, const: ConstStr):
        return const.value

    def visitConstInt(self, const: ConstInt):
        return const.value

    def visitVar(self, var: Var):
        return var.name






if __name__ == '__main__':
    teststr = '''\
if s[0] == 'a':
    assert len(s) == 1
else:
    assert s[1] == 'b'
    '''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    print(const.dump())
    cs = ConstraintSolver()
    print(cs.entrace(const))
    reg = re.compile(cs.entrace(const))
    s = 'a'
    print(re.match(reg, s))

