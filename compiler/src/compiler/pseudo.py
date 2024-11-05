from collections import namedtuple
from dataclasses import dataclass

memory = namedtuple("memory", "scope dtype")
register = namedtuple("register", "i")


@dataclass
class Int:
    data: int


@dataclass
class Id:
    data: str


@dataclass
class Add:
    lhs: Int
    rhs: Int
    op: str = "add"


@dataclass
class Mul:
    lhs: Int
    rhs: Int
    op: str = "mul"


BinOp = Add | Mul


@dataclass
class Let:
    identifier: Id
    value: Int | Add


Statement = Let


@dataclass
class Fn:
    args: list[Id]
    body: list[Statement]


@dataclass
class Return:
    value: Int


@dataclass
class AST:
    statements: list[Statement]


class Visitor:
    def __init__(self):
        self.symbols = {}
        self.scope = "global"

    def visit(self, ast):
        result = []
        for statement in ast.statements:
            result += self.visit_statement(statement)
        return result

    def visit_statement(self, statement):
        if self.is_let(statement):
            return self.visit_let(statement)
        if self.is_binop(statement):
            return self.visit_value(statement, 0)[0]
        else:
            raise Exception(f"Unknown statement: {statement}")

    def visit_let(self, let):
        key = let.identifier.data
        self.symbols[key] = memory(self.scope, dtype="int")
        instructions, addr = self.visit_value(let.value, 0)
        return instructions + [("mov", key, addr)]

    def visit_value(self, node, index):
        if self.is_int(node):
            addr = register(index)
            return [("mov", addr, node.data)], addr
        if self.is_identifier(node):
            addr = register(index)
            return [("mov", addr, node.data)], addr
        elif self.is_binop(node):
            lhs_instructions, addr = self.visit_value(
                node.lhs, index
            )
            lhs_index = addr.i
            rhs_instructions, addr = self.visit_value(
                node.rhs, lhs_index + 1
            )
            rhs_index = addr.i
            return lhs_instructions + rhs_instructions + [
                (
                    node.op,
                    register(lhs_index),
                    register(rhs_index),
                    register(rhs_index + 1),
                ),
            ], register(rhs_index + 1)
        else:
            raise Exception(f"Unknown value: {node}")

    @staticmethod
    def is_let(node):
        return isinstance(node, Let)

    @staticmethod
    def is_binop(node):
        return isinstance(node, BinOp)

    @staticmethod
    def is_add(node):
        return isinstance(node, Add)

    @staticmethod
    def is_int(node):
        return isinstance(node, Int)

    @staticmethod
    def is_identifier(node):
        return isinstance(node, Id)


ast = AST(
    [
        Let(Id("x"), Int(5)),
        Let(Id("t"), Fn([], [Return(Id("x"))])),
    ]
)

visitor = Visitor()
instructions = visitor.visit(ast)
print(visitor.symbols)
for instruction in instructions:
    print(instruction)
