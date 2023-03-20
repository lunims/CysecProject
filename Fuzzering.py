import ast
from TypeInferer import TypeInferer
from ConstraintSolver import ConstraintSolver
from fuzzingbook.Grammars import *
from fuzzingbook.GrammarFuzzer import *
import isla
from isla.solver import ISLaSolver
class FuzzerOfConstraints:
    pass

if __name__ == '__main__':
    teststr = '''\
def test(s):
    if s[0] == 'a':
        assert len(s) == 1
    else:
        assert len(s) != 3
        assert s[0] != 'z'
        assert s[1] == 'b'
        assert s[4] != 'm'
        assert s[7] != 't'
    '''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    cs = ConstraintSolver()
    gr = cs.entrance(constraint=const)
    print(gr)
    fuzz = GrammarFuzzer(gr)
    #print(fuzz.fuzz())
    #print(gr)
    solver = ISLaSolver(gr, '(str.len(<element0>) = 4) and str.len(<element1>) = 1')
    print(solver.solve())
    print(solver.solve())
    #solver = ISLaSolver(grammar, 'str.len(<int>) > 5')
    printi = set()
    for i in range(100):
        inp = fuzz.fuzz()
        if solver.check(inp):
            printi.add(inp)
    print(printi)

