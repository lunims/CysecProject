
from TypeInferer import TypeInferer
from ConstraintSolver import ConstraintSolver
from fuzzingbook.Grammars import *
from fuzzingbook.GrammarFuzzer import *
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
    cs = ConstraintSolver
    gr = cs.entrance(const)
    fuzz = GrammarFuzzer
    print(fuzz.fuzz_grammar(gr))

