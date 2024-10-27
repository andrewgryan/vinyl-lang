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
        try:
            return lhs + rhs
        except TypeError:
            return ("ADD", lhs, rhs)
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
    return ("EXIT", visit_expression(node.status))


def visit_print(node):
    return visit_expression(node.message)


def visit_let(node):
    expr = visit_expression(node.value)
    return (
        "LET",
        visit_identifier(node.identifier),
        visit_expression(node.value),
    )


def visit_function(node):
    pre = [("FUNCTION", "START")]
    post = [("FUNCTION", "END")]
    return pre + visit_statements(node.body.statements) + post


def visit_block(node):
    pre = [("BLOCK", "START")]
    post = [("BLOCK", "END")]
    return pre + visit_statements(node.statements) + post


def visit_identifier(node):
    return node.token.text


def visit_statements(statements):
    numbers = []
    for statement in statements:
        number = visit_statement(statement)
        if isinstance(number, list):
            numbers += number
        else:
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


def test_visitor():
    ast = parser.parse(
        """
        let x = 1 + 1 + 2 + 3;
        fn example() {
            let code = x + 16;
            {
                let scoped = 3;
            }
            exit(code);
        }

        let t = 10 * 10;
    """
    )
    assert is_let(ast.statements[1].body.statements[0])
    assert visit(ast) == [
        ("LET", "x", 7),
        ("FUNCTION", "START"),
        ("LET", "code", ("ADD", "x", 16)),
        ("BLOCK", "START"),
        ("LET", "scoped", 3),
        ("BLOCK", "END"),
        ("EXIT", "code"),
        ("FUNCTION", "END"),
        ("LET", "t", 100),
    ]


def gas(instructions):
    registers = {"r1": "rax"}
    for inst in instructions:
        if inst[0] == "LABEL":
            yield f"{inst[1]}:"
        elif inst[0] == "MOV":
            src = f"${inst[1]}"
            dst = f"%{registers[inst[2]]}"
            yield f"\tmov {src}, {dst}"


def aarch64(instructions):
    registers = {"r1": "x1"}
    for inst in instructions:
        if inst[0] == "LABEL":
            yield f"{inst[1]}:"
        elif inst[0] == "MOV":
            src = f"#{hex(inst[1])}"
            dst = f"{registers[inst[2]]}"
            yield f"\tmov {dst}, {src}"


def render(lines):
    return "\n".join(lines) + "\n"


def test_ir_code_gen():
    ir = [("LABEL", "L1"), ("MOV", 5, "r1")]
    assert list(gas(ir)) == ["L1:", "\tmov $5, %rax"]
    assert list(aarch64(ir)) == ["L1:", "\tmov x1, #0x5"]
