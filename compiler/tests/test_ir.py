from compiler import ir, parser
import pytest


@pytest.mark.parametrize(
    "code,expected",
    [
        ("return 5;", [(ir.RETF, ir.Lit(5))]),
        (
            "let x = 1;let y = 2;",
            [
                (
                    ir.COPY,
                    ir.Lit(1),
                    ir.Var("x", "u32", "_start"),
                ),
                (
                    ir.COPY,
                    ir.Lit(2),
                    ir.Var("y", "u32", "_start"),
                ),
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
    elif is_binop(node):
        return visit_binop(node)
    elif is_identifier(node):
        return visit_identifier(node)
    else:
        raise Exception(node)


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
    elif is_function(node):
        return visit_function(node)
    elif is_block(node):
        return visit_block(node)
    else:
        raise Exception(node)


def visit_exit(node):
    return visit_expression(node.status)


def visit_print(node):
    return visit_expression(node.message)


def visit_let(node):
    return visit_expression(node.value)


def visit_function(node):
    return visit_statements(node.body.statements)


def visit_block(node):
    return visit_statements(node.statements)


def visit_identifier(node):
    return 0


def visit_statements(statements):
    numbers = []
    for statement in statements:
        number = visit_statement(statement)
        numbers.append(number)
    return numbers


def visit(ast):
    return visit_statements(ast.statements)


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


def is_function(node):
    return isinstance(node, parser.NodeFunction)


def is_identifier(node):
    return isinstance(node, parser.NodeIdentifier)


def is_block(node):
    return isinstance(node, parser.NodeBlock)


@pytest.mark.skip("debug parser")
def test_visitor():
    ast = parser.parse("""
        let x = 1 + 1 + 2 + 3;
        fn example() {
            let code = 1 + 16;
            {
                let scoped = 3;
            }
            exit(code);
        }

        let t = 100;
    """)
    assert visit(ast) == [7, [17, [3], 0], 100]


def test_parse_nested_blocks():
    ast = parser.parse("""
        let x = 1 + 1 + 2 + 3;
        fn example() {
            let code = 1 + 16;
            {
                let scoped = 3;
            }
            exit(code);
        }

        let t = 100;
    """)
    print(ast.statements[1].body.statements[2])
    assert False
