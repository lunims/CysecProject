#import isla
#from isla.solver import ISLaSolver
import ast

from fuzzingbook.GrammarFuzzer import GrammarFuzzer
from fuzzingbook.Grammars import *
from isla.solver import ISLaSolver

import Constraintclasses
from Constraintclasses import *
from TypeInferer import TypeInferer


class ConstraintSolver:

    def __init__(self, code: ast.AST):
        self.constraint = ''
        ti = TypeInferer()
        const = ti.entrance(code)
        self.grammar = self.entrance(const)

    def entrance(self, constraint: Constraint):
        clear, dic = self.cleanUp(constraint, dict())
        dnf = self.to_dnf(clear)
        res = self.reg(dnf)
        res = self.cleanGrammar(self.cleanGrammar(res))
        return res

    def cleanGrammar(self, gr: Grammar):
        he = list()
        it = gr.keys()
        counterDigit = 0
        counterDigits = 0
        for k in gr:
            for i in it:
                for y in gr[i]:
                    if k in y:
                        he.append(k)
                        if k == '<digit>':
                            counterDigit += 1
                        if k == '<digits>':
                            counterDigits += 1
        res = list(set(it) - set(he))
        res.remove("<start>")
        for i in res:
            del gr[i]
        if counterDigit == 2 and counterDigits == 1:
            del gr['<digit>']
            del gr['<digits>']
        elif counterDigits == 1:
            del gr['<digits>']
        return gr

    def cleanUp(self, cons: Constraint, dic: dict()):
        match cons:
            case And():
                conl, dicl = self.cleanUp(cons.lhs, dic)
                conr, dicr = self.cleanUp(cons.rhs, dicl)
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
                    case ConstStr, ConstInt, ConstBool:
                        if isinstance(cons.rhs, ConstStr) or isinstance(cons.rhs, ConstInt) or isinstance(cons.rhs, ConstBool):
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





    def to_dnf(self, constraint: Constraint):
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
        constraintsCollecting = list()
        digit = list()
        for i in range(32, 127):
            digit.append(chr(i))
        grammar: Grammar = {
            "<start>": ['<string>'],
            "<string>": [],
            "<digits>": ["<digit>""<digits>", "<digit>"],
            "<digitsU>": ["", "<digits>"],
            "<digit>": digit,
            "<digitU>": ["", "<digit>"],
        }
        elementcount = 0
        for s in se:
            rdic, rndic, rset, startend= self.collectConstraint(s)
            if self.build_GrammarExpression(rdic, rndic, rset, startend, elementcount, digit) is not None:
                gramdict, constraint = self.build_GrammarExpression(rdic, rndic, rset, startend, elementcount, digit)
                res = gramdict.get("<string>")
                grammar["<string>"].append(res)
                del gramdict["<string>"]
                grammar.update(gramdict)
                elementcount += 1
                constraintsCollecting.append(constraint)
        flag = False
        for i in constraintsCollecting:
            if i != '':
                self.constraint += f'({i})'
                if flag:
                    self.constraint += ' and '
                flag = True
        return grammar

    def build_GrammarExpression(self, dic: dict(), ndic: dict(), se: set(), startend: set(), name: int, digit: list()):
        digit = list()
        for i in range(32, 127):
            digit.append(chr(i))
        resgram: Grammar = {
            "<string>": "<element" + str(name) + ">",
            "<element" + str(name) + ">": [],
            "<digits>": ["<digit>""<digits>", "<digit>"],
            "<digitsU>": ["", "<digits>"],
            "<digit>": digit,
            "<digitU>": ["", "<digit>"],
        }
        maxidic = 0
        maxindic = 0
        st = ''
        sf = 0
        et = ''
        ef = 0
        for s in startend:
            match s[0]:
                case 'st':
                    if len(s[1]) > len(st):
                        if s[1].startswith(st):
                            st = s[1]
                        else:
                            return None
                    else:
                        if not st.startswith(s[1]):
                            return None
                case 'et':
                    if len(s[1]) > len(et):
                        if s[1].endswith(et):
                            et = s[1]
                        else:
                            return None
                    else:
                        if not et.endswith(s[1]):
                            return None
                case 'sf':
                    sf = max(sf, len(s[1]))
                case 'ef':
                    ef = max(ef, len(s[1]))
                case _:
                    raise Exception("Falsches Set")
        common = ''
        for i in range(len(st)):
            if et.startswith(st[i:]):
                common = st[i:]
                break
        if len(common) != 0:
            resgram["<element" + str(name) + ">"].append(st + et[len(common):])
        maxse = (len(st) - len(common)) + (len(et) - len(common))
        for i in range(len(st)):
            if dic.keys():
                if i in dic.keys():
                    if dic[i] != st[i]:
                        return None
                else:
                    dic[i] = st[i]
            else:
                dic[i] = st[i]
        if dic.keys():
            maxidic = max(dic.keys())
        if ndic.keys():
            maxindic = max(ndic.keys())
        if self.getLength(se) is None:
            return None
        res = list()
        upper, lower, fix, nfix = self.getLength(se)
        if fix is not None:
            if fix > upper or fix < lower or fix in nfix or fix <= maxidic or fix <= maxse:
                return None
            else:
                for e in range(len(et)):
                    dic[fix - len(et) + e] = et[e]
                for i in range(fix):
                    res.append("<digit>")
        else:
            lower = max(maxidic + 1, lower + 1, maxse)
            for i in range(lower):
                res.append("<digit>")
            if upper != sys.maxsize and upper >= lower:
                while (len(res) < (upper - len(et))):
                    res.append("<digitU>")
                for e in list(et):
                    res.append(e)
            else:
                while (len(res) < (maxindic + 1 - len(et))):
                    res.append("<digitU>")
                if res[len(res) - 1] == "<digit>":
                    res[len(res) - 1] = "<digits>"
                else:
                    res.append("<digitsU>")
                for e in list(et):
                    res.append(e)
        for k in dic.keys():
            if res[k] in digit and res[k] != dic.get(k):
                return None
            res[k] = dic.get(k)
        namecount = 1
        for n in ndic.keys():
            if res[n] in digit and res[n] not in list(ndic[n]):
                pass
            elif res[n] in digit and res[n] in list(ndic[n]):
                return None
            else:
                if res[n].startswith("<digits>"):
                    res[n] = "<digitsU>"
                    res.insert(n, "<digit>")
                if res[n].startswith("<digitsU>"):
                    res.insert(n, "<digitU>")
                newname = "<digit"
                for i in range(namecount):
                    newname += str(name)
                newdigi = list()
                for i in range(32, 127):
                    newdigi.append(chr(i))
                for c in ndic[n]:
                    if c in newdigi:
                        newdigi.remove(str(c))
                if res[n].startswith("<digitU"):
                    res[n] = newname + "U>"
                    resgram[res[n]] = ["", newname + ">"]
                    resgram[newname + ">"] = newdigi
                else:
                    res[n] = newname + ">"
                    resgram[newname + ">"] = newdigi
                namecount += 1
        if sf != 0 or ef != 0:
            resgram = self.buildNegativeWithGrammar(resgram, res, startend, name)
        else:
            resgram["<element" + str(name) + ">"].append(''.join(res))
        cons = list()
        for i in nfix:
            if lower <= i <= upper:
                cons.append("not(str.len(<element" + str(name) + ">) = " + str(i) + ")")
        cons = " and ".join(cons)
        return resgram, cons

    def buildNegativeWithGrammar(self, resgram: Grammar, element: list(), negse: set(), name: int):
        if "<digits>" in element or "<digitsU>" in element:
            negs = list()
            nege = list()
            fixchar = dict()
            for n in negse:
                match n[0]:
                    case 'sf':
                        if len(n[1]) <= len(element):
                            negs.append(n[1])
                    case 'ef':
                        if len(n[1]) <= len(element):
                            nege.append(n[1])
            for e in range(len(element)):
                if len(element[e]) == 1:
                    fixchar[e] = element[e]
            for ns in negs:
                for test in range(len(ns)):
                    if test in fixchar.keys():
                        if ns[test] != fixchar.get(test):
                            negs.remove(ns)
            namecount = 1
            maxns = len(max(negs, key=len))
            catch = ""
            if len(element) <= maxns:
                catch = element[len(element) - 1]
                element[len(element) - 1] = "digit"
            while len(element) < maxns:
                element.append("<digit>")
            element.append(catch)
            for ns in negs:
                for s in range(len(ns)):
                    if len(element[s]) == 1:
                        pass
                    else:
                        newdigi = list()
                        newele = list()
                        newname = "<notelement"
                        newdigname = "<notdigit"
                        for i in range(namecount):
                            newname += str(name)
                            newdigname += str(name)
                        newname += ">"
                        newdigname += ">"
                        namecount += 1
                        for e in element:
                            newele.append(e)
                        for d in resgram[element[s]]:
                            newdigi.append(d)
                        newdigi.remove(ns[s])
                        newele[s] = newdigname
                        resgram["<element" + str(name) + ">"].append(newname)
                        resgram[newdigname] = newdigi
                        resgram[newname] = []
                        resgram[newname].append(''.join(newele))
            pass #TODO for endswith but very hard
        else:
            negs = list()
            nege = list()
            fixchar = dict()
            for n in negse:
                match n[0]:
                    case 'sf':
                        if len(n[1]) <= len(element):
                            negs.append(n[1])
                    case 'ef':
                        if len(n[1]) <= len(element):
                            nege.append(n[1])
            for e in range(len(element)):
                if len(element[e]) == 1:
                    fixchar[e] = element[e]
            for ns in negs:
                for test in range(len(ns)):
                    if test in fixchar.keys():
                        if ns[test] != fixchar.get(test):
                            negs.remove(ns)
            for ne in nege:
                for test in range(len(ne)):
                    if (len(element) - 1 - test)  in fixchar.keys():
                        if ne[len(ne) - 1 - test] != fixchar.get(len(element) - 1 - test):
                            nege.remove(ne)
            namecount = 1
            for ns in negs:
                for s in range(len(ns)):
                    if len(element[s]) == 1:
                        pass
                    else:
                        newdigi = list()
                        newele = list()
                        newname = "<notelement"
                        newdigname = "<notdigit"
                        for i in range(namecount):
                            newname += str(name)
                            newdigname += str(name)
                        newname += ">"
                        newdigname += ">"
                        namecount += 1
                        for e in element:
                            newele.append(e)
                        for d in resgram[element[s]]:
                            newdigi.append(d)
                        newdigi.remove(ns[s])
                        newele[s] = newdigname
                        resgram[newdigname] = newdigi
                        resgram["<element" + str(name) + ">"].append(newname)
                        resgram[newname] = []
                        resgram[newname].append(''.join(newele))
            for ne in nege:
                ne = ne[::-1]
                for e in range(len(ne)):
                    if len(element[len(element) - 1 - e]) == 1:
                        pass
                    else:
                        newdigi = list()
                        newele = list()
                        newname ="<notelement"
                        newdigname = "<notdigit"
                        for i in range(namecount):
                            newname += str(name)
                            newdigname += ">"
                        newname += ">"
                        newdigname += ">"
                        namecount += 1
                        for el in element:
                            newele.append(el)
                        for d in resgram[element[len(element) - 1 - e]]:
                            newdigi.append(d)
                        newdigi.remove(ne[e])
                        newele[len(element) - 1 - e] = newdigname
                        resgram[newdigname] = newdigi
                        resgram["<element" + str(name) + ">"].append(newname)
                        resgram[newname] = []
                        resgram[newname].append(''.join(newele))
        return resgram



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
            raise Exception()

    def visitAnd(self, a: And):
        dict1, ndict1, set1, startend1 = self.collectConstraint(a.lhs)
        dict2, ndict2, set2, startend2 = self.collectConstraint(a.rhs)
        for key in ndict1:
            if ndict2.get(key) != None:
                ndict1[key] = ndict1.get(key) + ndict2.get(key)
                del ndict2[key]
        resSet = set1.union(set2)
        resstartend = startend1.union(startend2)
        dict2.update(dict1)
        ndict2.update(ndict1)
        return dict2, ndict2, resSet, resstartend



    def visitNot(self, no: Not):
        dic, ndict, se, startend = self.collectConstraint(no.operand)
        resset = set()
        resstartend = set()
        for s in se:
            match s[0]:
                case '==':
                    resset.add(('!=', s[1]))
                case '!=':
                    resset.add(('==', s[1]))
                case '<':
                    resset.add(('>=', s[1]))
                case '<=':
                    resset.add(('>', s[1]))
                case '>':
                    resset.add(('<=', s[1]))
                case '>=':
                    resset.add(('<', s[1]))
        for ste in startend:
            match ste[0]:
                case 'sf':
                    resstartend.add(('st', ste[1]))
                case 'st':
                    resstartend.add(('sf', ste[1]))
                case 'ef':
                    resstartend.add(('et', ste[1]))
                case 'et':
                    resstartend.add(('ef', ste[1]))
        return ndict, dic, resset, resstartend

    def visitCompare(self, comp: Compare):
        if isinstance(comp.lhs, Call):
            if isinstance(comp.lhs.func, Constraintclasses.CharAt):
                return self.evalCharAt(comp.lhs, comp.rhs, comp.operator)
            elif isinstance(comp.lhs.func, Length):
                return self.evalLen(comp.rhs, comp.operator)
            elif isinstance(comp.lhs.func, Constraintclasses.startsWith):
                return self.evalStartsWith(comp.lhs, comp.rhs, comp.operator)
            elif isinstance(comp.lhs.func, Constraintclasses.EndsWith):
                return self.evalEndsWith(comp.lhs, comp.rhs, comp.operator)
            else:
                raise NotImplementedError
        elif isinstance(comp.lhs, Var):
            match comp.operator.operator:
                case ast.Eq():
                    return self.evalEquals(comp.rhs)
                case ast.NotEq():
                    return self.evalNotEquals(comp.rhs)
                case _:
                    raise NotImplementedError

    def evalEndsWith(self, lhs: Term, rhs: Term, op: Comparator):
        res = set()
        match op.operator:
            case ast.Eq() | ast.Is():
                if rhs.value:
                    res.add(('et', lhs.args[1].value))
                    return dict(), dict(), set(), res
                else:
                    res.add(('ef', lhs.args[1].value))
                    return dict(), dict(), set(), res
            case ast.NotEq():
                if rhs.value:
                    res.add(('ef', lhs.args[1].value))
                    return dict(), dict(), set(), res
                else:
                    res.add(('et', lhs.args[1].value))
                    return dict(), dict(), set(), res
            case _:
                raise NotImplementedError




    def evalStartsWith(self, lhs: Term, rhs: Term, op: Comparator):
        res = set()
        match op.operator:
            case ast.Eq():
                if rhs.value:
                    res.add(('st', lhs.args[1].value))
                    return dict(), dict(), set(), res
                else:
                    res.add(('sf', lhs.args[1].value))
                    return dict(), dict(), set(), res
            case ast.Is():
                if rhs.value:
                    res.add(('st', lhs.args[1].value))
                    return dict(), dict(), set(), res
                else:
                    res.add(('sf', lhs.args[1].value))
                    return dict(), dict(), set(), res
            case ast.NotEq():
                if rhs.value:
                    res.add(('sf', lhs.args[1].value))
                    return dict(), dict(), set(), res
                else:
                    res.add(('st', lhs.args[1].value))
                    return dict(), dict(), set(), res
            case _:
                raise NotImplementedError

    def visitEqual(self, equal: Equal):
        return dict(), dict(), set(), set()

    def evalCharAt(self, lhs: Call, rhs: ConstStr, op: Comparator):
        match op.operator:
            case ast.Eq():
                dic = dict()
                dic[lhs.args[1].value] = rhs.value
                return dic, dict(), set(), set()
            case ast.NotEq():
                dic = dict()
                dic[lhs.args[1].value] = rhs.value
                return dict(), dic, set(), set()
            case _:
                raise NotImplementedError


    def evalLen(self, rhs: ConstInt, op: Comparator):
        match op.operator:
            case ast.Eq():
                return dict(), dict(), {('==', rhs.value)}, set()
            case ast.NotEq():
                return dict(), dict(), {('!=', rhs.value)}, set()
            case ast.Lt():
                return dict(), dict(), {('<', rhs.value)}, set()
            case ast.LtE():
                return dict(), dict(), {('<=', rhs.value)}, set()
            case ast.Gt():
                return dict(), dict(), {('>', rhs.value)}, set()
            case ast.GtE():
                return dict(), dict(), {('>=', rhs.value)}, set()
            case _:
                raise NotImplementedError

    def evalEquals(self, rhs: ConstStr):
        dic = dict()
        counter = 0
        for i in list(rhs.value):
            dic[counter] = i
            counter += 1
        se = set()
        se.add(('==', counter))
        return dic, dict(), se, set()

    def evalNotEquals(self, rhs: ConstStr):
        return dict(), dict(), set(), set()








if __name__ == '__main__':
    teststr = '''\
def test(s):
    if s[0] == 'a':
        assert len(s) == 1
    '''
    teststr2 = '''\
def test(s):
    if s.startsWith("test"):
        x = True
        assert s.startsWith("te") == x
        assert len(s) == 6
        assert s != "tester"
    else:
        assert len(s) != 3
        assert s[0] != 'z'
        assert s[1] == 'b'
        assert s[4] != 'm'
        assert s[7] != 't'
    '''
    test2 = '''\
def test2(s):
    x = 5
    y = x
    s == y
    z = y
    s == z
'''
    cs = ConstraintSolver(code=ast.parse(teststr))
    print(cs.grammar)
    solver = ISLaSolver(cs.grammar, 'str.len(<element0>) = 6')
    fuzz = GrammarFuzzer(cs.grammar)
    printi = set()
    for i in range(100):
        inp = fuzz.fuzz()
        #print(inp)
        if solver.check(inp):
            printi.add(inp)
    print(printi)
