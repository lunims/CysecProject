import ast
from TypeInferer import TypeInferer
from ConstraintSolver import ConstraintSolver
from fuzzingbook.Grammars import *
from fuzzingbook.GrammarFuzzer import *
import isla
from isla.solver import ISLaSolver
import Constraintclasses
from Constraintclasses import *
import argparse
from pathlib import Path

def fuzzing(grammar: Grammar, constraint: str, size:int):
    fuzz = GrammarFuzzer(grammar)
    solver = None
    if constraint == '':
        solver = ISLaSolver(grammar)
    else:
        solver = ISLaSolver(grammar, constraint)
    printi = set()
    for i in range(size):
        inp = fuzz.fuzz()
        if solver.check(inp):
            printi.add(inp)
    print(printi)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("-g", "--grammar", action="store_true")
    parser.add_argument("-c", "--constraint", action="store_true")
    parser.add_argument("-f", "--fuzz")

    args = parser.parse_args()
    gr = args.grammar
    c = args.constraint
    target_dir = Path(args.path)

    if not target_dir.exists():
        print("The target directory does not exist")
        raise SystemExit(1)

    with open(target_dir, 'r') as f:
        source_code = f.read()
    tree = ast.parse(source_code)

    cs = ConstraintSolver(code=tree)

    if c:
        if cs.constraint == '':
            print("There is no additional constraint for ISLa")
        else:
            print(cs.constraint)

    if gr:
        print(cs.grammar)

    if args.fuzz != None:
        fuzzing(grammar=cs.grammar, constraint=cs.constraint, size=int(args.fuzz))