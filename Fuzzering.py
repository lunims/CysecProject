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
        assert s[0] != 'z'
        assert s[1] == 'b'
    '''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    cs = ConstraintSolver()
    gr = cs.entrance(constraint=const)
    print(gr)
    fuzz = GrammarFuzzer(gr)
    #print(fuzz.fuzz())
    #print(gr)
    solver = ISLaSolver(gr, 'not(str.len(<digitsU>) = 3)')
    print(solver.solve())
    print(solver.solve())
    grammar = {'<start>': ['<config>'], '<config>': ['pagesize=<pagesize>\nbufsize=<bufsize>'], '<pagesize>': ['<int>'],
               '<bufsize>': ['<int>'], '<int>': ['<leaddigit><digits>'], '<digits>': ['', '<digit><digits>'],
               '<digit>': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
               '<leaddigit>': ['1', '2', '3', '4', '5', '6', '7', '8', '9']}
    #solver = ISLaSolver(grammar, 'str.len(<int>) > 5')
    for i in range(100):
        inp = fuzz.fuzz()
        if solver.check(inp):
            print(inp)

