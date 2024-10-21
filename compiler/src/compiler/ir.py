from dataclasses import dataclass

COPY = "COPY"
RETF = "RETF"


@dataclass
class Lit:
    value: int


@dataclass
class Var:
    name: str
    type: str
    owner: str


def translate(ast):
    ops = []
    for statement in ast.statements:
        if hasattr(statement, "identifier"):
            id = statement.identifier.text
            value = int(statement.value.token.text)
            op = (
                COPY,
                Lit(value),
                Var(id, "u32", "_start"),
            )
        else:
            op = (RETF, Lit(5))
        ops.append(op)
    return ops
