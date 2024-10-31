"""
Intermediate representation
"""
from compiler import parser


def gas(instructions):
    for (op, arg1, arg2, result) in instructions:
        if op == "=":
            yield f"mov ${arg2}, -0x8(%rbp)"
        elif op == "exit":
            yield f"mov $60, %rax"
            yield f"mov ${arg1}, %rdi"
            yield f"syscall"
        elif op == "return":
            yield f"mov ${arg1}, %rax"
            yield f"ret"
        elif (op, arg1) == ("program", "start"):
            yield ".global _start"
            yield ".text"
            yield "_start:"


def aarch64(instructions):
    for (op, arg1, arg2, result) in instructions:
        if op == "=":
            yield f"mov [sp, #0x8], #{hex(arg2)}"
        elif op == "exit":
            yield f"mov x8, #0x5d"
            yield f"mov x0, #{hex(arg1)}"
            yield f"svc 0"
        elif op == "return":
            yield f"mov x0, #{hex(arg1)}"
            yield f"ret"
        elif (op, arg1) == ("program", "start"):
            yield ".global _start"
            yield ".section .text"
            yield ""
            yield "_start:"


def render(lines):
    return "\n".join(lines) + "\n"


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
        yield from visit_return(node)
    else:
        raise Exception(node)


def visit_exit(node):
    return [
        ("exit", visit_expression(node.status), None, None)
    ]


def visit_print(node):
    return visit_expression(node.message)


def visit_let(node):
    expr = visit_expression(node.value)
    yield (
        "=",
        visit_identifier(node.identifier),
        visit_expression(node.value),
        None
    )


def visit_function(node):
    yield from visit_statements(node.body.statements)


def visit_block(node):
    yield from visit_statements(node.statements)


def visit_identifier(node):
    return node.token.text


def visit_statements(statements):
    for statement in statements:
        yield from visit_statement(statement)


def visit_return(node):
    yield ("return", visit_expression(node.expression), None, None)


def visit(ast):
    if is_program(ast):
        yield ("program", "start", None, None)
        yield from visit_statements(ast.statements)
        yield ("program", "end", None, None)


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
