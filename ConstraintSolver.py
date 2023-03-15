#import isla
#from isla.solver import ISLaSolver
import re
import Constraintclasses
from Constraintclasses import *
import ast
from TypeInferer import TypeInferer


class ConstraintSolver:

    def entrace(self, constraint: Constraint):
        clear, dic = self.cleanUp(constraint, dict())
        #print(clear.dump())
        dnf = self.to_dnf(clear)
        res = self.reg(dnf)
        return res

    def cleanUp(self, cons: Constraint, dic: dict()):
        match cons:
            case And():
                conl, dicl = self.cleanUp(cons.lhs, dic)
                conr, dicr =self.cleanUp(cons.rhs, dicl)
                return And(conl, conr), dicr
            case Or():
                conl, dicl = self.cleanUp(cons.lhs, dic)
                conr, dicr = self.cleanUp(cons.rhs, dic)
                return Or(conl, conr), dic
            case Not():
                con, dicn = self.cleanUp(cons.operand, dic)
                return Not(con), dic
            case Equal():
                if isinstance(cons.value, Var):
                    if cons.value.name in dic:
                        cons.value = dic[cons.value.name]
                dic[cons.name.name] = cons.value
                return cons, dic
            case Compare():
                match cons.lhs:
                    case ConstStr, ConstInt:
                        if isinstance(cons.rhs, ConstStr) or isinstance(cons.rhs, ConstInt):
                            return cons, dic
                        he = cons.lhs
                        cons.lhs = cons.rhs
                        cons.rhs = he
                        return self.cleanUp(cons, dic)
                    case Var():
                        if cons.lhs.name in dic:
                            cons.lhs = dic[cons.lhs.name]
                    case Call():
                        for i in cons.lhs.args:
                            if isinstance(i, Var):
                                if i.name in dic:
                                    i = dic[i.name]
                    case _:
                        raise Exception("Geht nicht!")
                match cons.rhs:
                    case Var():
                        if cons.rhs.name in dic:
                            cons.rhs = dic[cons.rhs.name]
                    case Call():
                        for i in cons.rhs.args:
                            if isinstance(i, Var()):
                                if i.name in dic:
                                    i = dic[i.name]
                return cons, dic





    def to_dnf(self, constraint):
        # base case: if the constraint is a Compare or an Equal, return it as a set
        if isinstance(constraint, (Compare, Equal)):
            return {constraint}

        # if the constraint is a Not, negate its operand and return it as a set
        if isinstance(constraint, Not):
            negated = self.to_dnf(constraint.operand)
            return {Not(c) for c in negated}

        # recursively apply the DNF conversion to the left and right operands
        lhs = self.to_dnf(constraint.lhs)
        rhs = self.to_dnf(constraint.rhs)

        # if the constraint is an Or, distribute it over the operands using the union of sets
        if isinstance(constraint, Or):
            return lhs.union(rhs)

        # if the constraint is an And, distribute it over the operands using the Cartesian product of sets
        if isinstance(constraint, And):
            result = set()
            for l in lhs:
                for r in rhs:
                    result.add(And(l, r))
            return result

    def reg(self, set: {}):
        res = ''
        flag = False
        for i in set:
            if flag:
                res += ' | '
            #res += self.build_regex(self.collectConstraint(i))
            dic, ndic, se = self.collectConstraint(i)
            #print(dic)
            #print(ndic)
            #print(se)
            flag = True
        return res

    def build_regex(self, cons: (dict, {})):
        pass

    def collectConstraint(self, constraint: Constraint):
        if isinstance(constraint, And):
            return self.visitAnd(constraint)
        elif isinstance(constraint, Not):
            return self.visitNot(constraint)
        elif isinstance(constraint, Equal):
            return self.visitEqual(constraint)
        elif isinstance(constraint, Compare):
            return self.visitCompare(constraint)
        else:
            raise Exception

    def visitAnd(self, a: And):
        dict1, ndict1, set1 = self.collectConstraint(a.lhs)
        dict2, ndict2, set2 = self.collectConstraint(a.rhs)
        for key in ndict1:
            if ndict2.get(key) != None:
                ndict1[key] = ndict1.get(key) + ndict2.get(key)
                del ndict2[key]
        resSet = set1.union(set2)
        dict2.update(dict1)
        ndict2.update(ndict1)
        return dict2, ndict2, resSet



    def visitNot(self, no: Not):
        dic, ndict, se = self.collectConstraint(no.operand)
        return ndict, dic, se

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
        '''s = equal.value.value
        res = {}
        i = 0
        for c in s:
            res[i] = c
            i += 1'''
        #TODO: if name == input then egal
        return dict(), dict(), set()

    def evalCharAt(self, lhs: Call, rhs: ConstStr, op: Comparator):
        match op.operator:
            case ast.Eq():
                dic = {}
                dic[lhs.args[1].value] = rhs.value
                return dic, dict(), set()
            case ast.NotEq():
                dic = {}
                dic[lhs.args[1].value] = rhs.value
                return dict(), dic, set()
            case _:
                raise NotImplementedError


    def evalLen(self, rhs: ConstInt, op: Comparator):
        match op.operator:
            case ast.Eq():
                return dict(), dict(), {('==', rhs.value)}
            case ast.NotEq():
                return dict(), dict(), {('!=', rhs.value)}
            case ast.Lt():
                return dict(), dict(), {('<', rhs.value)}
            case ast.LtE():
                return dict(), dict(), {('<=', rhs.value)}
            case ast.Gt():
                return dict(), dict(), {('>', rhs.value)}
            case ast.GtE():
                return dict(), dict(), {('>=', rhs.value)}
            case _:
                raise NotImplementedError

    def evalEquals(self, rhs: ConstStr):
        return dict(), dict(), set()

    def evalNotEquals(self, rhs: ConstStr):
        return dict(), dict(), set()








if __name__ == '__main__':
    teststr = '''\
def test(s):
    if s[0] == 'a':
        assert len(s) == 1
    else:
        assert s[0] != 'z'
        assert s[1] == 'b'
    '''
    test2 = '''\
def test2(s):
    x = 5
    y = x
    s == y
    z = y
    s == z
'''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    #print(const.dump())
    cs = ConstraintSolver()
    for i in cs.to_dnf(const):
        print(i.dump())
    print(cs.entrace(const))
    #reg = re.compile(cs.entrace(const))
    #s = 'a'
    #cont = ti.entrance(ast.parse(test2))
    #print(cont.dump())
    #cs.entrace(cont)

