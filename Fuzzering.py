import ast
from TypeInferer import TypeInferer
from ConstraintSolver import ConstraintSolver
from fuzzingbook.Grammars import *
from fuzzingbook.GrammarFuzzer import *
import isla
from isla.solver import ISLaSolver
class FuzzerOfConstraints:
    def gimmeResults(self, code: ast.AST):
        cs = ConstraintSolver(code)
        print(cs.grammar)
        print(cs.constraint)
        fuzz = GrammarFuzzer(cs.grammar)
        solver = None
        if cs.constraint == '':
            solver = ISLaSolver(cs.grammar)
        else:
            solver = ISLaSolver(cs.grammar, cs.constraint)
        #print(cs.constraint)
        print(solver.solve())
        print(solver.solve())
        printi = set()
        for i in range(100):
            inp = fuzz.fuzz()
            if solver.check(inp):
                printi.add(inp)
        print(printi)

if __name__ == '__main__':
    test1 = '''\
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
    test2 = '''\
if s[0] == 'a':
    if s[1] == 'b':
        if s[2] == 'c':
            if s[3] == 'd':
                assert len(s) == 4
            else:
                assert s[3] == 'i'
        else:
            assert len(s) == 3
            assert s[2] != 'd'
else:
    if s[0] == 'z':
        assert len(s) == 1
    else:
        assert s.startsWith("boing")
        assert len(s) == 6
    '''
    test3 = '''\
if len(s) == 1:
    assert s[0] != 'a'
    assert s[0] != 'b'
    assert s[0] != 'c'
    assert s[0] != 'd'
    assert s[0] != 'e'
    assert s[0] != 'f'
    assert s[0] != 'g'
    assert s[0] != 'h'
    assert s[0] != 'i'
    assert s[0] != 'j'
    assert s[0] != 'k'
    assert s[0] != 'l'
    assert s[0] != 'm'
    assert s[0] != 'n'
    assert s[0] != 'o'
else:
    assert s[0] != 'A'
    assert s[1] == 'A'
    assert s[2] != 'A'
    assert s[3] == '('
    '''
    testi = '''
if len(s) < 10:
    if s.startsWith('efg'):
        assert s.endsWith('fghi')
    else:
        assert s[2] == 'g'
    '''


    fuzziman = FuzzerOfConstraints
    #fuzziman.gimmeResults(fuzziman, ast.parse(test1.py))
    #fuzziman.gimmeResults(fuzziman, ast.parse(test2))
    #fuzziman.gimmeResults(fuzziman, ast.parse(test3))
    fuzziman.gimmeResults(fuzziman, ast.parse(testi))

