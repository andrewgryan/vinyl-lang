"""
Intermediate representation
"""
from compiler import parser


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
    return [
        ("exit", visit_expression(node.status), None, None)
    ]
    # return ("EXIT", visit_expression(node.status))


def visit_print(node):
    return visit_expression(node.message)


def visit_let(node):
    expr = visit_expression(node.value)
    return (
        "=",
        visit_identifier(node.identifier),
        visit_expression(node.value),
        None
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
