from compiler import ir, parser
import pytest


@pytest.mark.parametrize(
    "code,expected",
    [
        ("return 5;", [(ir.RETF, ir.Lit(5))]),
        (
            "let x = 1;let y = 2;",
            [
                (ir.COPY, ir.Lit(1), ir.Var("x", "u32", "_start")),
                (ir.COPY, ir.Lit(2), ir.Var("y", "u32", "_start")),
            ],
        ),
    ],
)
def test_ir(code, expected):
    ast = parser.parse(code)
    actual = ir.translate(ast)
    assert actual == expected


def visit_int(node):
    return int(node.token.text)


def visit_expression(node):
    if is_int(node):
        return visit_int(node)
    else:
        return visit_binop(node)


def visit_binop(binop):
    lhs = visit_expression(binop.lhs)
    rhs = visit_expression(binop.rhs)
    if binop.operator.operator == "+":
        return lhs + rhs
    elif binop.operator.operator == "*":
        return lhs * rhs


def visit_statement(node):
    if is_exit(node):
        return visit_exit(node)
    elif is_let(node):
        return visit_let(node)
    elif is_print(node):
        return visit_print(node)


def visit_exit(node):
    return visit_expression(node.status)


def visit_print(node):
    return visit_expression(node.message)


def visit_let(node):
    return visit_expression(node.value)


def is_exit(node):
    return isinstance(node, parser.NodeExit)


def is_print(node):
    return isinstance(node, parser.NodePrint)


def is_binop(node):
    return isinstance(node, parser.NodeBinOp)


def is_int(node):
    return isinstance(node, parser.NodeInt)


def is_let(node):
    return isinstance(node, parser.NodeLet)


def visit(ast):
    result = 0
    for statement in ast.statements:
        status = visit_statement(statement)
        result = max(status, result)
    return result

def test_visitor():
    ast = parser.parse("exit(2 * 6 + 1); print(10 + 10); let x = 17;")
    assert visit(ast) == 20
