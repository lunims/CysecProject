import isla
from isla.solver import ISLaSolver
import ast
from TypeInferer import TypeInferer


class ConstraintSolver():

    def __init__(self, cons: str, name: str, variables: set()):
        self.constraint = cons
        self.name = name
        self.variables = variables
        self.supported = ['charAt', 'startswith', 'endswith', 'len', 'equals', 'regex', 'assert']

    def clean(self):
        help = self.constraint.split(' OR ')
        res = []
        for h in help:
            useful = set()
            useful.add(self.name)
            s = h.replace('(', ' ')
            s = s.replace(')', ' ')
            s = s.replace('.', ' ')
            if (' ' + self.name + ' ') in s:
                useful = self.parts(s)
            res.append(self.polish(h, useful))
        res.remove('')
        self.constraint = ' OR '.join(res)
        l = self.constraint.count('(')
        r = self.constraint.count(')')
        self.constraint = self.constraint[l-r:]
        print(self.constraint)

    def polish(self, h: str, useful: set()):
        help = h.split(' AND ')
        res = []
        for i in help:
            s = i.replace('(', ' ')
            s = s.replace(')', ' ')
            s = s.replace('.', ' ')
            comp = s.split(' ')
            flag = False
            for c in comp:
                if c in useful:
                    flag = True
            if flag == True:
                res.append(i)
        return ' AND '.join(res)



    def parts(self, s: str):
        useful = set()
        useful.add((self.name))
        help = s.split(' AND ')
        for i in help:
            comp = i.split(' ')
            flag = False
            for c in comp:
                if c in useful:
                    flag = True
            if flag == True:
                for v in self.variables:
                    if (v) in comp:
                        useful.add(v)
        return useful


if __name__ == '__main__':
    teststr = '''\
def test(s):
    if s[0] == 'a':
        assert len(s) == 1
        x = s
        x = y
        z = "test"
        assert s.startswith("test")
    else:
        jockel = 5
        s[0] = jockel
        assert s[1] == 'b'
'''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    print(const)
    print(ti.getVariables())
    print(ti.getName())
    cs = ConstraintSolver(cons=const, name=ti.getName(), variables=ti.getVariables())
    cs.clean()
