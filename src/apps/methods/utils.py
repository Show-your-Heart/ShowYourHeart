import re


def parse_expression_dependencies(expr: str):
    keywords = ["val", "true", "false", "and", "AND", "&&", "or", "OR", "||", "null"]

    tokens = expr.split()

    dependencies = []
    for token in tokens:
        if re.match(r"^[a-zA-Z]\w*", token):  # variable
            if "_" in token:
                subtokens = re.split(r"[_]", token)
                dependencies.append(subtokens[0])
            elif token in keywords:  # ignore keywords
                continue
            else:
                dependencies.append(token)

    return dependencies
