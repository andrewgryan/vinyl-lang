from collections import namedtuple
from dataclasses import dataclass

memory = namedtuple("memory", "scope dtype")


@dataclass
class Register:
    index: int


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
        return instructions + [("=", key, addr)]

    def visit_value(self, node, index):
        if self.is_int(node):
            addr = Register(index)
            return [("mov", node.data, addr)], addr
        if self.is_identifier(node):
            addr = Register(index)
            return [("mov", node.data, addr)], addr
        elif self.is_binop(node):
            lhs_instructions, addr = self.visit_value(
                node.lhs, index
            )
            lhs_index = addr.index
            rhs_instructions, addr = self.visit_value(
                node.rhs, lhs_index + 1
            )
            rhs_index = addr.index
            return lhs_instructions + rhs_instructions + [
                (
                    node.op,
                    Register(lhs_index),
                    Register(rhs_index),
                    Register(rhs_index + 1),
                ),
            ], Register(rhs_index + 1)
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
        Let(
            Id("x"),
            Int(5)
        ),
        Let(
            Id("y"),
            Int(6)
        ),
        Add(Id("x"), Id("y"))
    ]
)

visitor = Visitor()
instructions = visitor.visit(ast)
print(visitor.symbols)
for instruction in instructions:
    print(instruction)
