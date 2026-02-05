import re


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
        if re.match(r"^[a-zA-Z]\w*", token):  # variable
            if "_" in token:
                subtokens = re.split(r"[_]", token)
                dependencies.append(subtokens[0])
            else:
                dependencies.append(token)

    return dependencies
