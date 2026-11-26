import re
from dataclasses import dataclass

@dataclass
class Token:
    kind: str
    value: str
    line: int
    column: int

class Lexer:
    # This lexer intentionally supports a small educational subset of C.
    TOKEN_RE = re.compile(
        r'(?P<SPACE>[ \t\r]+)|(?P<NEWLINE>\n)|'
        r'(?P<COMMENT>//[^\n]*|/\*[\s\S]*?\*/)|'
        r'(?P<STRING>"(?:\\.|[^"\\])*")|'
        r"(?P<CHAR>'(?:\\.|[^'\\])*')|"
        r'(?P<NUMBER>\d+(?:\.\d+)?)|'
        r'(?P<ID>[A-Za-z_]\w*)|'
        r'(?P<OP>==|!=|<=|>=|&&|\|\||\+\+|--|[+\-*/%=<>!])|'
        r'(?P<PUNCT>[(){};,])|(?P<OTHER>.)'
    )
    KEYWORDS = {"int", "float", "double", "char", "void", "if", "else",
                "while", "for", "return", "printf", "scanf"}

    def __init__(self, source):
        self.source = source

    def scan(self):
        tokens, errors = [], []
        line = column = 1
        for match in self.TOKEN_RE.finditer(self.source):
            kind, value = match.lastgroup, match.group()
            start_line, start_col = line, column
            line_count = value.count("\n")
            if kind == "NEWLINE":
                line += 1
                column = 1
                continue
            if kind in {"SPACE", "COMMENT"}:
                if line_count:
                    line += line_count
                    column = len(value.rsplit("\n", 1)[-1]) + 1
                else:
                    column += len(value)
                continue
            if kind == "OTHER":
                errors.append({
                    "phase": "Lexical", "line": start_line, "column": start_col,
                    "message": f"Unexpected character {value!r}.",
                    "suggestion": "Remove it or replace it with a valid C token."
                })
            else:
                if kind == "ID" and value in self.KEYWORDS:
                    kind = "KEYWORD"
                tokens.append(Token(kind, value, start_line, start_col))
            if line_count:
                line += line_count
                column = len(value.rsplit("\n", 1)[-1]) + 1
            else:
                column += len(value)
        tokens.append(Token("EOF", "", line, column))
        return tokens, errors
