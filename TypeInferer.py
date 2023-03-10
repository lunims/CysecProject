import ast
from Constraintclasses import *


class TypeInferer(ast.NodeVisitor):
    def __init__(self):
        self.constraints = None
        self.name = ''
        self.variables = set()

    def getName(self):
        return self.name

    def getVariables(self):
        return self.variables
    def entrance(self, node: ast):
        self.constraints = self.visit(node)
        return self.constraints

    def visit_FunctionDef(self, node: ast.FunctionDef):
        andi = self.visit(node.body[0])
        for n in node.body[1:]:
            andi =And(left = andi, right = self.visit(n))
        return andi

    def visit_If(self, node: ast.If):
        compcons = self.visit(node.test)
        ifcons = compcons
        elsecons = Not(compcons)
        for b in node.body:
            ifcons = And(ifcons, self.visit(b))
        for e in node.orelse:
            elsecons = And(elsecons, self.visit(e))
        res = Or(ifcons, elsecons)
        return res

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        op = node.ops[0]
        if len(node.comparators) > 1:
            right = self.visit(ast.Compare(node.comparators[0], node.ops[1:], node.comparators[1:]))
        else:
            right = self.visit(node.comparators[0])
        res = Compare(op, left, right)
        return res

    def visit_Constant(self, node: ast.Constant):
        res = None
        if isinstance(node.value, str):
            res = ConstStr(node.value)
        elif isinstance(node.value, int):
            res = ConstInt(node.value)
        else:
            raise NotImplementedError
        return res

    def visit_Name(self, node: ast.Name):
        res = Var(node.id)
        return res

    def visit_Subscript(self, node: ast.Subscript):
        arguments = list()
        arguments = arguments.append(self.visit(node.value))
        arguments = arguments.append(self.visit(node.slice))
        res = Call(CharAt, arguments)
        return res


    def visit_Assert(self, node: ast.Assert):
        return self.visit(node.test)

    def visit_Call(self, node: ast.Call):
        name = ''
        res = None
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            raise Exception('Gibts nicht!')
        match name:
            case 'len':
                res = Length
            case _:
                return None
        reslist = list()
        for i in node.args:
            reslist.append(self.visit(i))
        return Call(res, reslist)

    def visit_While(self, node: ast.While):
        self.visit(node.test)
        for i in node.body:
            self.visit(i)
        for j in node.orelse:
            self.visit(j)
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
        x = 5
        s[0] = x
        assert s[1] == 'b'
'''
    ti = TypeInferer()
    print(ti.entrance(ast.parse(teststr)))
