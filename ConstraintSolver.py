import isla
from isla.solver import ISLaSolver
import ast
from TypeInferer import TypeInferer


class ConstraintSolver:

    def __init__(self, cons: str, name: str, variables: {}):
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
        var = self.constraint.split(' OR ')        # split our constraint by OR
        res = []
        for h in var:
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
        left = self.constraint.count('(')
        right = self.constraint.count(')')
        self.constraint = self.constraint[left - right:]   # remove excessive brackets from the beginning
        print(self.constraint)

    """
    polish(self, h: str, useful: set())
        This method is called in clean().
        It deletes every unnecessary part of the substring we give to this method
    """

    def polish(self, h: str, useful: {}):
        var = h.split(' AND ')                     # split string by AND
        res = []
        for i in var:
            s = i.replace('(', ' ')
            s = s.replace(')', ' ')
            s = s.replace('.', ' ')                 # remove unnecessary characters
            comp = s.split(' ')
            flag = False
            for c in comp:
                if c in useful:                     # check if one component is in useful
                    flag = True                     # useful is a set of variables connected to our input string
            if flag:
                res.append(i)
        return ' AND '.join(res)                    # join result list to String again

    """
    parts(self, s: str)
        This method is called in clean()
        It returns all variables that are connected to our input in the given string
    """

    def parts(self, s: str):
        useful = set()                            # useful is set with variables connected to our input
        useful.add(self.name)                     # useful starts with input string
        var = s.split(' AND ')
        for i in var:
            comp = i.split(' ')
            flag = False
            for c in comp:
                if c in useful:                   # check if component is in useful
                    flag = True
            if flag:                              # if True add all variables of component to our useful set
                for v in self.variables:
                    if v in comp:
                        useful.add(v)
        return useful

    def updateVariables(self):
        print(self.variables)
        collector = self.constraint.replace('(', ' ')
        collector = collector.replace(')', ' ')
        collector = collector.replace('.', ' ')
        store = set()
        for v in self.variables:
            if (' ' + v + ' ') in collector:
                store.add(v)
        self.variables = store
        print(self.variables)


    def createrOfGrammar(self):
        with open('grammar.py', 'w') as gram:
            gram.truncate(0)
            gram.write('grammar = {')
            comps = self.getComponentsL(self.constraint)
            while len(comps) > 2:
                if comps[1] == 'AND':
                    self.createCombinedGrammar(gram, comps[0])
                if comps[1] == 'OR':
                    self.createDijunctGrammar(gram, comps[0])



    def getComponentsL(self, cons: str):
        res = list()
        countbrackets = 0
        countstart = 0
        countend = 0
        opflag = False
        oper = ''
        z = 0
        for i in cons:
            countend += 1
            if opflag:
                if i == 'A':
                    oper += i
                    countstart += 1
                if i == 'N':
                    oper += i
                    countstart += 1
                if i == 'D':
                    oper += i
                    countstart += 1
                if i == 'O':
                    oper += i
                    countstart += 1
                if i == 'R':
                    oper += i
                    countstart += 1
                if i == ' ':
                    countstart += 1
                    z += 1
                    if z == 2:
                        res.append(oper)
                        oper = ''
                        z = 0
                        opflag = False
            else:
                if i == '(':
                    countbrackets += 1
                if i == ')':
                    countbrackets -= 1
                if countbrackets == 0:
                    opflag = True
                    res.append(cons[countstart:countend])
                    countstart = countend
        print(res)
        return res





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
        j = 5
        s[0] = j
        assert s[1] == 'b'
'''
    ti = TypeInferer()
    const = ti.entrance(ast.parse(teststr))
    #print(const)
    #print(ti.getVariables())
    #print(ti.getName())
    cs = ConstraintSolver(cons=const, name=ti.getName(), variables=ti.getVariables())
    cs.clean()
    cs.updateVariables()
    cs.getComponentsL(cs.constraint)
