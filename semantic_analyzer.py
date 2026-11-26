from error_handler import make_error

NUMERIC_TYPES = {"int", "float", "double"}

class SemanticAnalyzer:
    def __init__(self, statements):
        self.statements = statements
        self.symbols = {}

    def analyze(self):
        errors = []
        for stmt in self.statements:
            kind = stmt["kind"]
            if kind == "declaration":
                name = stmt["name"]
                token = stmt["name_token"]
                if name in self.symbols:
                    errors.append(make_error("Semantic", token,
                        f"Variable {name!r} is declared more than once.",
                        "Use a different name or remove the duplicate declaration."))
                else:
                    self.symbols[name] = stmt["type"]
                errors.extend(self.check_expression(stmt.get("initializer")))
            elif kind == "assignment":
                name = stmt["name"]
                if name not in self.symbols:
                    errors.append(make_error("Semantic", stmt["name_token"],
                        f"Variable {name!r} is used before it is declared.",
                        f"Declare it first, for example: int {name};"))
                errors.extend(self.check_expression(stmt.get("expression")))
            elif kind == "return":
                errors.extend(self.check_expression(stmt.get("expression")))
            elif kind == "call":
                for arg in stmt.get("args", []):
                    errors.extend(self.check_expression(arg))
        return errors

    def check_expression(self, expr):
        errors = []
        if not expr:
            return errors
        for part in expr.get("parts", []):
            if isinstance(part, dict) and part.get("kind") == "identifier":
                name = part["value"]
                if name not in self.symbols:
                    errors.append(make_error("Semantic", part["token"],
                        f"Variable {name!r} is used before it is declared.",
                        f"Declare {name} before using it."))
            elif isinstance(part, dict) and "right" in part:
                right = part.get("right")
                if right and right.get("kind") == "identifier":
                    name = right["value"]
                    if name not in self.symbols:
                        errors.append(make_error("Semantic", right["token"],
                            f"Variable {name!r} is used before it is declared.",
                            f"Declare {name} before using it."))
        return errors
