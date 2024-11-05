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
        else:
            raise Exception(f"Unknown value: {value}")

    @staticmethod
    def is_let(node):
        return isinstance(node, Let)

    @staticmethod
    def is_add(node):
        return isinstance(node, Add)

    @staticmethod
    def is_int(node):
        return isinstance(node, Int)


ast = AST([
  # Let(Id("x"), Add(Add(Int(5), Int(6)), Int(7))),
  Let(Id("y"), Int(12)),
  Let(Id("z"), Int(24))
])

visitor = Visitor()
instructions = visitor.visit(ast)
print(visitor.symbols)
for instruction in instructions:
    print(instruction)
