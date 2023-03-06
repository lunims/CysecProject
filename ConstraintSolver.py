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
        useful = set().add(self.name)
        help = self.constraint.split(' OR ')
        help = help.split(' AND ')
        for h in help:
            h = h.replace('(', ' ')
            h = h.replace(')', ' ')
            h = h.replace('.', ' ')
            for u in useful:
                if (' ' + u + ' ') in h:
                    useful.union(self.parts(h))

    def parts(self, s: str):
        for op in self.supported:
            s = s.replace(op, '')
        help = s.split(' ')
        res = set()
        for h in help:
            if h != '' and h[0] != "'" and h.isdigit() == False:
                res.add(h)
        return res




if __name__ == '__main__':
    teststr = '''\
def test(s):
    if s[0] == 'a':
        assert len(s) == 1
        x = y
        z = "test"
        assert s.startswith("test")
    else:
        assert s[1] == 'b'
'''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    print(const)
    print(ti.getVariables())
    cs = ConstraintSolver(cons=const, name=ti.getName(), variables=ti.getVariables())


