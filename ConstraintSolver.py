#import isla
#from isla.solver import ISLaSolver
import re
import sys

import Constraintclasses
from Constraintclasses import *
import ast
from TypeInferer import TypeInferer
from typing import List, Dict, Union, Any, Tuple, Optional
from fuzzingbook.Grammars import *


class ConstraintSolver:

    def entrance(self, constraint: Constraint):
        clear, dic = self.cleanUp(constraint, dict())
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

    def reg(self, se: {}):
        digit = list()
        for i in range(128):
            digit.append(chr(i))
        digiti = digit
        digiti.append("")
        grammar: Grammar = {
            "<start>": [],
            "<digits>": ["<digits>""<digit>", "<digit>"],
            "<digits?>": ["", "<digits>"],
            "<digit>": digit,
            "<digit?>": digiti,
        }
        elementcount = 0
        for s in se:
            rdic, rndic, rset = self.collectConstraint(s)
            if self.build_GrammarExpression(rdic, rndic, rset, elementcount, digit) is not None:
                gramdict, nfix, ndicover = self.build_GrammarExpression(rdic, rndic, rset, elementcount, digit)
                res = gramdict.get("<start>")
                grammar["<start>"].append(res)
                del gramdict["<start>"]
                grammar.update(gramdict)
                elementcount += 1
        return grammar

    def build_GrammarExpression(self, dic: dict(), ndic: dict(), se: set(), name: int, digit: list()):
        if self.getLength(se) is None:
            return None
        resgram: Grammar = {
            "<start>": [],
        }
        res = list()
        ndicover = dict()
        upper, lower, fix, nfix = self.getLength(se)
        if fix is not None:
            if fix > upper or fix < lower or fix in nfix or fix <= max(dic.keys()):
                return None
            else:
                for i in range(fix):
                    res.append("<digit>")
        else:
            for u in dic.keys():
                if lower < u:
                    lower = u
            for i in range(lower + 1):
                res.append("<digit>")
            if upper != sys.maxsize:
                while (len(res) < upper):
                    res.append("<digit?>")
        for k in dic.keys():
            if res[k] in digit and res[k] != dic.get(k):
                return None
            res[k] = dic.get(k)
        namecount = 1
        for n in ndic.keys():
            if n >= len(res):
                ndicover[n] = ndic[n]
            elif res[n] in digit and res[n] not in list(ndic[n]):
                pass
            elif res[n] in digit and res[n] in list(ndic[n]):
                return None
            else:
                newdigi = digit
                for c in ndic[n]:
                    if c in newdigi:
                        newdigi.remove(str(c))
                newname = "<digit"
                for i in range(namecount):
                    newname += str(name)
                newname += ">"
                res[n] = newname
                resgram[newname] = newdigi
                namecount += 1
        if upper == sys.maxsize and fix is None:
            if res[len(res) - 1] == "<digit>":
                res[len(res - 1)] = "<digits>"
            else:
                res.append("<digits?>")
        resgram["<start>"] = ''.join(res)
        return resgram, nfix, ndicover

    def getLength(self, se: set()):
        upper = sys.maxsize
        lower = 0
        fix = None
        nfix = list()
        for s in se:
            match s[0]:
                case '==':
                    if fix is None:
                        fix = s[1]
                    else:
                        return None
                case '<=':
                    if upper > s[1]:
                        upper = s[1]
                case '!=':
                    nfix.append(s[1])
                case '>=':
                    if lower < s[1]:
                        lower = s[1]
                case '<':
                    if upper > s[1]:
                        upper = s[1] - 1
                case '>':
                    if lower < s[1]:
                        lower = s[1] + 1
        return upper, lower, fix, nfix

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

    def visitCompare(self, comp: Compare):
        if isinstance(comp.lhs, Call):
            if comp.lhs.func is Constraintclasses.CharAt:
                return self.evalCharAt(comp.lhs, comp.rhs, comp.operator)
            elif comp.lhs.func is Length:
                return self.evalLen(comp.rhs, comp.operator)
            else:
                raise NotImplementedError
        elif isinstance(comp.lhs, Var):
            match comp.operator:
                case ast.Eq:
                    return self.evalEquals(comp.rhs)
                case ast.NotEq:
                    return self.evalNotEquals(comp.rhs)
                case _:
                    raise NotImplementedError

    def visitEqual(self, equal: Equal):
        return dict(), dict(), set()

    def evalCharAt(self, lhs: Call, rhs: ConstStr, op: Comparator):
        match op.operator:
            case ast.Eq():
                dic = dict()
                dic[lhs.args[1].value] = rhs.value
                return dic, dict(), set()
            case ast.NotEq():
                dic = dict()
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
    #for i in cs.to_dnf(const):
        #print(i.dump())
    gram = cs.entrance(const)
    #reg = re.compile(cs.entrace(const))
    for i in range(100):
        print(simple_grammar_fuzzer(gram))


