import re

from django.db.models import F, Q


def parse_expression_dependencies(expr: str):
    # Replace logical operators
    expr = expr.replace("&&", " and ")

    # Handle chained comparisons: 0 <= X <= ind1
    expr = re.sub(
        r"(\w+)\s*<=\s*(\w+)\s*<=\s*(\w+)", r"(\1 <= \2) and (\2 <= \3)", expr
    )

    tokens = expr.split()

    dependencies = []
    for token in tokens:
        if re.match(r"^[a-zA-Z_]\w*$", token):  # variable
            dependencies.append(token)

    return dependencies


def eval_expression(expr: str):
    # Replace logical operators
    expr = expr.replace("&&", " and ")

    # Handle chained comparisons: 0 <= X <= ind1
    expr = re.sub(
        r"(\w+)\s*<=\s*(\w+)\s*<=\s*(\w+)", r"(\1 <= \2) and (\2 <= \3)", expr
    )

    # Replace variables with Django F() objects
    tokens = expr.split()

    django_expr = []

    for token in tokens:
        if re.match(r"^[a-zA-Z_]\w*$", token):  # variable
            django_expr.append(f'F("{token}")')

        elif token in ["<=", ">=", "<", ">", "=", "=="]:
            if token == "=":
                token = "=="

            django_expr.append(token)

        else:
            django_expr.append(token)

    django_code = " ".join(django_expr)

    return eval(django_code, {"Q": Q, "F": F})
