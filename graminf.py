from ConstraintSolver import ConstraintSolver
from fuzzingbook.GrammarFuzzer import *
from isla.solver import ISLaSolver
from Constraintclasses import *
import argparse
from pathlib import Path


def fuzzing(grammar: Grammar, constraint: str, size: int):
    fuzz = GrammarFuzzer(grammar)
    if constraint == '':
        solver = ISLaSolver(grammar)
    else:
        solver = ISLaSolver(grammar, constraint)
    printi = set()
    for i in range(size):
        inp = fuzz.fuzz()
        if solver.check(inp):
            printi.add(inp)
    return printi


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("-g", "--grammar", action="store_true")
    parser.add_argument("-c", "--constraint", action="store_true")
    parser.add_argument("-f", "--fuzz", type=int)
    parser.add_argument("-comp", "--compile", action="store_true")

    args = parser.parse_args()
    gr = args.grammar
    c = args.constraint
    comp = args.compile
    source_dir = Path(args.path)

    if not source_dir.exists():
        print("The target directory does not exist")
        raise SystemExit(1)

    with open(source_dir, 'r') as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    function_def = next((node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)), None)
    function_name = function_def.name if function_def else None

    cs = ConstraintSolver(code=tree)

    if c:
        if cs.constraint == '':
            print("There is no additional constraint for ISLa")
        else:
            print(f'Additional ISLa Constraint: {cs.constraint}')

    if gr:
        print(cs.grammar)

    out = None

    if args.fuzz is not None:
        out = fuzzing(grammar=cs.grammar, constraint=cs.constraint, size=args.fuzz)
        print(f'Generated following set of inputs for function "{function_name}":')
        print(out)

    if comp:
        if out is None:
            out = fuzzing(grammar=cs.grammar, constraint=cs.constraint, size=42)
        codeObject = compile(tree, source_dir, 'exec')
        exec(codeObject)
        function = locals()[function_name]
        num_errors = 0
        for i in out:
            try:
                function(i)
            except Exception as e:
                num_errors += 1
                print(f'Error: {e} with input:{i}')
        print(f'Ran function "{function_name}" a total number of {len(out)} times')
        print(f'Erros occured: {num_errors}')
