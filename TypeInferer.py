import ast
import isla
from isla.solver import ISLaSolver


class TypeInferer(ast.NodeVisitor):
    def __init__(self):
        self.constraints = ''
        self.name = ''
        self.variables = set()

    def getName(self):
        return self.name

    def getVariables(self):
        return self.variables
    def entrance(self, node: ast):
        self.visit(node)
        return self.constraints

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for arg in node.args.args:
            self.name = arg
            break
        flag = False
        for n in node.body:
            if flag:
                self.constraints += ' AND '
            self.visit(n)
            flag = True
        return None

    def visit_If(self, node: ast.If):
        self.visit(node.test)
        for b in node.body:
            self.constraints = self.constraints + ' AND '
            self.visit(b)
        for e in node.orelse:
            self.constraints = '(' + self.constraints + ')' + ' OR '
            self.visit(e)
        return None

    def visit_Compare(self, node: ast.Compare):
        self.constraints += '('
        self.visit(node.left)
        i = 0
        for r in node.comparators:
            op = ''
            opast = ast.dump(node.ops[i])
            if opast == 'Eq()':
                op = '=='
            if opast == 'NotEq()':
                op = '!='
            if opast == 'Lt()':
                op = '<'
            if opast == 'LtE()':
                op = '<='
            if opast == 'Gt()':
                op = '>'
            if opast == 'GtE()':
                op = '>='
            if opast == 'Is()':
                op = 'is'
            if opast == 'IsNot()':
                op = 'is not'
            if opast == 'In()':
                op = 'in'
            if opast == 'NotIn()':
                op = 'not in'
            self.constraints += ' ' + op + ' '
            i = i + 1
            self.visit(r)
        self.constraints += ')'
        return None

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, str):
            self.constraints += "'"
            self.constraints += str(node.value)
            self.constraints += "'"
        else:
            self.constraints += str(node.value)
        return None

    def visit_Name(self, node: ast.Name):
        self.variables.add(node.id)
        self.constraints += node.id
        return None

    def visit_Subscript(self, node: ast.Subscript):
        self.visit(node.value)
        self.constraints += '.charAt('
        self.visit(node.slice)
        self.constraints += ')'
        return None

    def visit_Assert(self, node: ast.Assert):
        self.visit(node.test)
        return None

    def visit_Call(self, node: ast.Call):
        self.visit(node.func)
        self.constraints += '('
        flag = False
        for arg in node.args:
            if flag:
                self.constraints += ', '
            self.visit(arg)
            flag = True
        self.constraints += ')'
        return None

    def visit_While(self, node: ast.While):
        self.visit(node.test)
        self.constraints += '('
        flag = False
        for i in node.body:
            if flag:
                self.constraints += ' AND '
            flag = True
            self.visit(i)
        for j in node.orelse:
            self.constraints += ' AND '
            self.visit(j)
        self.constraints += ')'
        return None

    def visit_For(self, node: ast.For):
        self.visit(node.iter)
        self.constraints += '('
        flag = False
        for i in node.body:
            if flag:
                self.constraints += ' AND '
            flag = True
            self.visit(i)
        for j in node.orelse:
            self.constraints += ' AND '
            self.visit(j)
        self.constraints += ')'
        return None

    def visit_Expr(self, node: ast.Expr):
        self.visit(node.value)
        return None

    def visit_ClassDef(self, node: ast.ClassDef):
        flag = False
        for b in node.body:
            if flag:
                self.constraints += ' OR '
            self.visit(b)
            flag = True
        return None

    def visit_Return(self, node: ast.Return):
        self.constraints += '('
        self.visit(node.value)
        self.constraints += ')'
        return None

    def visit_Assign(self, node: ast.Assign):
        self.constraints += '('
        flag = False
        for v in node.targets:
            if flag:
                self.constraints += ' AND '
            self.visit(v)
            self.constraints += ' = '
            self.visit(node.value)
        self.constraints += ')'
        return None

    def visit_Match(self, node: ast.Match):
        self.constraints += '('
        flag = False
        for i in node.cases:
            if flag:
                self.constraints += ' OR '
            self.visit(node.subject)
            self.constraints += ' == '
            self.visit(i)
            flag = True
        self.constraints += ')'
        return None

    def visit_Try(self, node: ast.Try):
        flag1 = False
        for i in node.body:
            if flag1:
                self.constraints += ' AND '
            self.visit(i)
            flag1 = True
        flag2 = True
        for j in node.orelse:
            if flag2:
                self.constraints += ' OR '
            else:
                self.constraints += ' AND '
            flag2 = False
            self.visit(j)
        for k in node.finalbody:
            self.constraints += ' AND '
            self.visit(k)
        return None

    def visit_BoolOp(self, node: ast.BoolOp):
        self.constraints += '('
        self.visit(node.values[0])
        for v in node.values[1:]:
            if ast.dump(node.op) == 'And()':
                self.constraints += ' And '
            else:
                self.constraints += ' Or '
            self.visit(v)
        self.constraints += ')'
        return None

    def visit_NamedExpr(self, node: ast.NamedExpr):
        self.visit(node.value)
        return None

    def visit_BinOp(self, node: ast.BinOp):
        self.constraints += '('
        self.visit(node.left)
        t = ast.dump(node.op)
        if t == 'Add()':
            self.constraints += ' + '
        if t == 'Sub()':
            self.constraints += ' - '
        if t == 'Mult()':
            self.constraints += ' * '
        if t == 'MatMult()':
            self.constraints += ' @ '
        if t == 'Div()':
            self.constraints += ' / '
        if t == 'Mod()':
            self.constraints += ' % '
        if t == 'Pow()':
            self.constraints += ' ** '
        if t == 'LShift()':
            self.constraints += ' << '
        if t == 'RShift()':
            self.constraints += ' >> '
        if t == 'BitOr()':
            self.constraints += ' | '
        if t == 'BitXor()':
            self.constraints += ' ^ '
        if t == 'BitAnd()':
            self.constraints += ' & '
        if t == 'FloorDiv()':
            self.constraints += ' // '
        self.visit(node.right)
        self.constraints += ')'
        return None

    def visit_UnaryOp(self, node: ast.UnaryOp):
        self.constraints += '('
        u = ast.dump(node.op)
        if u == 'Invert()':
            self.constraints += ' ~'
        if u == 'Not()':
            self.constraints += ' not'
        if u == 'UAdd()':
            self.constraints += ' +'
        if u == 'USub()':
            self.constraints += ' -'
        self.visit(node.operand)
        self.constraints += ')'
        return None

    def visit_IfExp(self, node: ast.IfExp):
        self.constraints += '('
        self.visit(node.test)
        self.constraints += ')'
        self.constraints += ' AND '
        self.constraints += '('
        self.visit(node.body)
        self.constraints += ')'
        self.constraints += ' OR '
        self.constraints += '('
        self.visit(node.orelse)
        self.constraints += ')'
        return None

    def visit_Attribute(self, node: ast.Attribute):
        self.visit(node.value)
        self.constraints += '.' + node.attr
        return None


if __name__ == '__main__':
    teststr = '''\
def test(s):
    if s[0] == 'a':
        assert len(s) == 1
    else:
        assert s[1] == 'b'
'''
    ti = TypeInferer()
    print(ti.entrance(ast.parse(teststr)))
