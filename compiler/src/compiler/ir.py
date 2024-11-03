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


def visit_statement(node, symbol_table=None):
    if is_exit(node):
        yield from visit_exit(node)
    elif is_let(node):
        yield from visit_let(node)
    elif is_print(node):
        yield from visit_print(node)
    elif is_function(node):
        yield from visit_function(node)
    elif is_block(node):
        yield from visit_block(node)
    elif is_return(node):
        yield from visit_return(node, symbol_table)
    elif is_call(node):
        yield from visit_call(node)
    else:
        raise Exception(node)


def visit_exit(node):
    status = visit_expression(node.status)
    assert isinstance(status, int)
    return [("exit", status, None, None)]


def visit_print(node):
    return visit_expression(node.message)


def visit_let(node):
    expr = visit_expression(node.value)
    yield (
        "=",
        visit_identifier(node.identifier),
        visit_expression(node.value),
        None,
    )


def visit_function(node):
    symbol_table = {}

    yield ("label", node.identifier.token.text, None, None)
    if len(node.parameters) > 0:
        yield ("prolog", 8 * len(node.parameters), None, None)
    # Stack assign parameters
    for i, parameter in enumerate(node.parameters, 1):
        symbol_table[parameter.token.text] = i
        yield ("parameter", i, 8, None)
    # TODO: stack allocate local variables
    for statement in node.body.statements:
        yield from visit_statement(statement, symbol_table)
    if len(node.parameters) > 0:
        yield ("epilog", 8 * len(node.parameters), None, None)
    yield ("ret", None, None, None)


def visit_block(node):
    yield from visit_statements(node.statements)


def visit_identifier(node):
    return node.token.text


def visit_statements(statements):
    for statement in statements:
        yield from visit_statement(statement)


def visit_return(node, symbol_table=None):
    status = visit_expression(node.expression)
    print(symbol_table, status)
    yield (
        "return",
        status,
        None,
        None,
    )


def visit_call(node):
    for i, value in enumerate(node.values, 1):
        yield (
            "store_parameter",
            i,
            visit_expression(value),
            None,
        )
    yield ("call", node.identifier.token.text, None, None)


def visit(ast):
    yield ("global", "start", None, None)
    yield ("section", "text", None, None)
    if is_program(ast):
        yield from visit_statements(
            statement
            for statement in ast.statements
            if is_function(statement)
        )
        yield ("label", "_start", None, None)
        yield from visit_statements(
            statement
            for statement in ast.statements
            if not is_function(statement)
        )


def is_program(node):
    return isinstance(node, parser.NodeProgram)


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


def is_return(node):
    return isinstance(node, parser.NodeReturn)


def is_call(node):
    return isinstance(node, parser.NodeCall)
