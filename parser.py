from error_handler import make_error

TYPE_WORDS = {"int", "float", "double", "char", "void"}

class Parser:
    """Recursive-descent parser for a deliberately small C-like subset."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.statements = []

    def current(self):
        return self.tokens[min(self.pos, len(self.tokens) - 1)]

    def advance(self):
        token = self.current()
        if token.kind != "EOF":
            self.pos += 1
        return token

    def accept(self, value):
        if self.current().value == value:
            return self.advance()
        return None

    def expect(self, value, explanation=None):
        if self.current().value == value:
            return self.advance()
        t = self.current()
        message = explanation or f"Expected {value!r}, but found {t.value!r}."
        suggestion = f"Insert {value!r} before {t.value!r}." if value == ";" else f"Check this statement; expected {value!r}."
        self.errors.append(make_error("Syntax", t, message, suggestion))
        return None

    def parse(self):
        # Accept the common entry-point wrapper: int main() { ... }
        if (len(self.tokens) >= 5
                and self.tokens[0].value == "int"
                and self.tokens[1].value == "main"
                and self.tokens[2].value == "("
                and self.tokens[3].value == ")"
                and self.tokens[4].value == "{"):
            self.pos = 5

        while self.current().kind != "EOF":
            before = self.pos
            if self.current().value == "}":
                self.advance()
            elif self.current().value in TYPE_WORDS:
                self.parse_declaration()
            elif self.current().value == "return":
                self.parse_return()
            elif self.current().value == "printf":
                self.parse_call()
            elif self.current().kind == "ID":
                self.parse_assignment()
            else:
                t = self.current()
                self.errors.append(make_error(
                    "Syntax", t, f"Unexpected token {t.value!r} at the start of a statement.",
                    "Start with a type declaration, variable assignment, printf(...), or return."
                ))
                self.advance()
            if self.pos == before:  # recovery guard
                self.advance()
        return self.statements

    def parse_declaration(self):
        typ = self.advance()
        name = self.current()
        if name.kind != "ID":
            self.errors.append(make_error("Syntax", name, "Expected a variable name after the type.",
                                          "Add an identifier, for example: int total;"))
            self.recover_statement()
            return
        self.advance()
        initializer = None
        if self.accept("="):
            initializer = self.parse_expression()
        self.expect(";")
        self.statements.append({"kind": "declaration", "type": typ.value,
                                "name": name.value, "name_token": name,
                                "initializer": initializer, "token": typ})

    def parse_assignment(self):
        name = self.advance()
        if not self.accept("="):
            self.errors.append(make_error("Syntax", self.current(),
                                          f"Expected '=' after variable {name.value!r}.",
                                          f"Use {name.value} = expression;"))
            self.recover_statement()
            return
        expr = self.parse_expression()
        self.expect(";")
        self.statements.append({"kind": "assignment", "name": name.value,
                                "name_token": name, "expression": expr, "token": name})

    def parse_return(self):
        token = self.advance()
        expr = None if self.current().value == ";" else self.parse_expression()
        self.expect(";")
        self.statements.append({"kind": "return", "expression": expr, "token": token})

    def parse_call(self):
        token = self.advance()
        self.expect("(")
        args = []
        if self.current().value != ")":
            args.append(self.parse_expression())
            while self.accept(","):
                args.append(self.parse_expression())
        self.expect(")")
        self.expect(";")
        self.statements.append({"kind": "call", "name": "printf", "args": args, "token": token})

    def parse_expression(self):
        # Basic expression parser: operands joined by operators.
        first = self.parse_operand()
        parts = [first] if first is not None else []
        while self.current().kind == "OP" and self.current().value not in {"++", "--"}:
            op = self.advance()
            right = self.parse_operand()
            parts.append({"operator": op.value, "right": right, "token": op})
            if right is None:
                break
        return {"kind": "expression", "parts": parts} if parts else None

    def parse_operand(self):
        t = self.current()
        if t.kind in {"NUMBER", "STRING", "CHAR"}:
            self.advance()
            return {"kind": "literal", "value": t.value, "token": t}
        if t.kind == "ID":
            self.advance()
            return {"kind": "identifier", "value": t.value, "token": t}
        if self.accept("("):
            expr = self.parse_expression()
            self.expect(")")
            return expr
        self.errors.append(make_error("Syntax", t, f"Expected an expression, found {t.value!r}.",
                                      "Provide a number, variable, string, or parenthesized expression."))
        if t.kind != "EOF":
            self.advance()
        return None

    def recover_statement(self):
        while self.current().kind != "EOF" and self.current().value != ";":
            self.advance()
        self.accept(";")
