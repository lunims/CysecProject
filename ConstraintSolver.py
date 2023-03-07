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

    """
    clean(self):
        This method is used to remove unnecessary parts of our constraint
        help methods: polish(), parts()
    """

    def clean(self):
        help = self.constraint.split(' OR ')        # split our constraint by OR
        res = []
        for h in help:
            useful = set()
            useful.add(self.name)
            s = h.replace('(', ' ')
            s = s.replace(')', ' ')
            s = s.replace('.', ' ')                 # removal of unnecessary characters
            if (' ' + self.name + ' ') in s:        # check if input string name is in our substring
                useful = self.parts(s)
            res.append(self.polish(h, useful))
        res.remove('')                              # remove empty parts of the list
        self.constraint = ' OR '.join(res)
        l = self.constraint.count('(')
        r = self.constraint.count(')')
        self.constraint = self.constraint[l - r:]   # remove excessive brackets from the beginning
        print(self.constraint)

    """
    polish(self, h: str, useful: set())
        This method is called in clean().
        It deletes every unnecessary part of the substring we give to this method
    """

    def polish(self, h: str, useful: set()):
        help = h.split(' AND ')                     # split string by AND
        res = []
        for i in help:
            s = i.replace('(', ' ')
            s = s.replace(')', ' ')
            s = s.replace('.', ' ')                 # remove unnecessary characters
            comp = s.split(' ')
            flag = False
            for c in comp:
                if c in useful:                     # check if one component is in useful
                    flag = True                     # useful is a set of variables connected to our input string
            if flag == True:
                res.append(i)
        return ' AND '.join(res)                    # join result list to String again

    """
    parts(self, s: str)
        This method is called in clean()
        It returns all variables that are connected to our input in the given string
    """

    def parts(self, s: str):
        useful = set()                              # useful is set with variables connected to our input
        useful.add((self.name))                     # useful starts with input string
        help = s.split(' AND ')
        for i in help:
            comp = i.split(' ')
            flag = False
            for c in comp:
                if c in useful:                     # check if component is in useful
                    flag = True
            if flag == True:                        # if True add all variables of component to our useful set
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
