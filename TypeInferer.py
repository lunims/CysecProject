import ast

import Constraintclasses
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

    def visit_Module(self, node: ast.Module):
        return self.visit(node.body[0])

    def visit_FunctionDef(self, node: ast.FunctionDef):
        andi = self.visit(node.body[0])
        for n in node.body[1:]:
            if self.visit(n) is not None:
                andi =And(left = andi, right = self.visit(n))
        return andi

    def visit_If(self, node: ast.If):
        compcons = self.visit(node.test)
        if isinstance(compcons, Constraintclasses.Call):
            compcons = Constraintclasses.Compare(op=Comparator(op=ast.Eq()), left=compcons, right=ConstBool(val=True))
        ifcons = compcons
        elsecons = None
        if len(node.orelse) != 0:
            elsecons = Not(compcons)
        for b in node.body:
            if self.visit(b) is not None:
                ifcons = And(ifcons, self.visit(b))
        for e in node.orelse:
            if self.visit(e) is not None:
                elsecons = And(elsecons, self.visit(e))
        if elsecons is None:
            return ifcons
        else:
            return Or(ifcons, elsecons)

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        op = Comparator(node.ops[0])
        res = None
        if len(node.comparators) > 1:
            rightterm = self.visit(node.comparators[0])
            rightcompare = self.visit(ast.Compare(rightterm, node.ops[1:], node.comparators[1:]))
            comp = Compare(op, left, rightterm)
            res = And(comp, rightcompare)
        else:
            right = self.visit(node.comparators[0])
            res = Compare(op, left, right)
        return res

    def visit_Constant(self, node: ast.Constant):
        res = None
        if isinstance(node.value, str):
            res = ConstStr(node.value)
        elif isinstance(node.value, bool):
            res = ConstBool(node.value)
        elif isinstance(node.value, int):
            res = ConstInt(node.value)
        else:
            raise NotImplementedError
        return res

    def visit_Name(self, node: ast.Name):
        res = Var(node.id)
        return res

    def visit_Subscript(self, node: ast.Subscript):
        arguments = []
        arguments.append(self.visit(node.value))
        arguments.append(self.visit(node.slice))
        res = Call(CharAt(), arguments)
        return res


    def visit_Assert(self, node: ast.Assert):
        res = self.visit(node.test)
        if isinstance(res, Constraintclasses.Call):
            res = Compare(op=Comparator(op=ast.Eq()),
                          left=res,
                          right=ConstBool(True))
        return res

    def visit_Call(self, node: ast.Call):
        name = ''
        res = None
        reslist = list()
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
            reslist.append(self.visit(node.func.value))
        else:
            raise Exception('Gibts nicht!')
        match name:
            case 'len':
                res = Length()
            case 'startswith':
                res = startsWith()
            case 'endswith':
                res = EndsWith()
            case _:
                return None
        for i in node.args:
            reslist.append(self.visit(i))
        return Call(res, reslist)

    def visit_While(self, node: ast.While):
        comp = self.visit(node.test)
        andi = comp
        for i in node.body:
            andi = And(andi, self.visit(i))
        notcomp = Not(comp)
        bandi = notcomp
        for j in node.orelse:
            bandi = And(bandi, self.visit(j))
        res = And(andi, bandi)
        return res

    def visit_For(self, node: ast.For):
        res = None
        if len(node.body) >= 1:
            andi = self.visit(node.body[0])
            for i in node.body[1:]:
                andi = And(andi, self.visit(i))
            if len(node.orelse) >= 1:
                bandi = self.visit(node.orelse[0])
                for j in node.orelse[1:]:
                    bandi = And(bandi, self.visit(j))
                res = And(andi, bandi)
            else:
                res = andi
        else:
            if len(node.orelse) >= 1:
                bandi = self.visit(node.orelse[0])
                for j in node.orelse[1:]:
                    bandi = And(bandi, self.visit(j))
                res = bandi
            else:
                res = None
        return res

    def visit_Expr(self, node: ast.Expr):
        return self.visit(node.value)


    #dont needed but tried
    def visit_ClassDef(self, node: ast.ClassDef):
        if len(node.body) >= 1:
            ori = self.visit(node.body[0])
            for b in node.body[1:]:
                ori =  Or(ori, self.visit(b))
            return ori
        return None


    def visit_Return(self, node: ast.Return):
        res = self.visit(node.value)
        if isinstance(res, Constraintclasses.ConstBool):
            res = None
        return res

    def visit_Assign(self, node: ast.Assign):
        val = self.visit(node.value)
        res = Equal(self.visit(node.targets[0]), val)
        return res

    def visit_Match(self, node: ast.Match):
        sub = self.visit(node.subject)
        resl = list()
        for i in node.cases:
            newcomp = Compare(ast.Eq(), sub, self.visit(i))
            resl.append(newcomp)
        res = resl[0]
        if len(resl) > 1:
            for r in resl[1:]:
                res = Or(res, r)
        return res

    def visit_Try(self, node: ast.Try):
        andi1 = andi2 = andi3 = res = None
        if len(node.body) >= 1:
            andi1 = self.visit(node.body[0])
            for i in node.body[1:]:
                andi1 = And(andi1, self.visit(i))
        if len(node.orelse) >= 1:
            andi2 = self.visit(node.orelse[0])
            for j in node.orelse[1:]:
                andi2 = And(andi2, self.visit(j))
        if len(node.finalbody) >= 1:
            andi3 = self.visit(node.finalbody[0])
            for k in node.finalbody:
                andi3 = And(andi3, self.visit(k))
        if andi1 is not None:
            res = andi1
            if andi2 is not None:
                res = Or(res, andi2)
            if andi3 is not None:
                res = And(res, andi3)
        elif andi2 is not None:
            res = andi2
            if andi3 is not None:
                res = And(res, andi3)
        elif andi3 is not None:
            res = andi3
        return res

    def visit_BoolOp(self, node: ast.BoolOp):
        left = self.visit(node.values[0])
        right = self.visit(node.values[1])
        if isinstance(left, Constraintclasses.Call):
            left = Compare(op=Comparator(op=ast.Eq()),
                           left=left,
                           right=ConstBool(val=True))
        if isinstance(right, Constraintclasses.Call):
            right = Compare(op=Comparator(op=ast.Eq()),
                           left=right,
                           right=ConstBool(val=True))
        op = node.op.__class__.__name__
        res = None
        if len(node.values) > 2:
            rightres = self.visit(ast.BoolOp(node.op, node.values[1:]))
            if op == 'Or':
                leftres = Or(left, right)
                res = Or(leftres, rightres)
            if op == 'And':
                leftres = And(left, right)
                res = And(leftres, rightres)
        else:
            if op == 'Or':
                res = Or(left, right)
            if op == 'And':
                res = And(left, right)
        return res


    def visit_NamedExpr(self, node: ast.NamedExpr):
        res = Equal(self.visit(node.target),self.visit(node.value))
        return res

    def visit_UnaryOp(self, node: ast.UnaryOp):
        resval = self.visit(node.operand)
        res = Not(resval)
        return res

    def visit_IfExp(self, node: ast.IfExp):
        comp = self.visit(node.test)
        if isinstance(comp, Constraintclasses.Call):
            comp = Compare(op=Comparator(op=ast.Eq()),
                           left=comp,
                           right=ConstBool(val=True))
        andi = self.visit(node.body)
        ori = self.visit(node.orelse)
        res = Or(And(comp, andi), ori)
        return res

    def visit_Attribute(self, node: ast.Attribute): #hardcode needed functioncalls
        var = self.visit(node.value)
        match node.attr:
            case 'startswith':
                #return Startswith
                pass
            case 'endswith':
                #return Endswith
                pass
            case _:
                raise NotImplementedError

        return None


