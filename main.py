from pathlib import Path
import argparse
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from error_handler import print_report

def analyze(source: str):
    tokens, lexical_errors = Lexer(source).scan()
    parser = Parser(tokens)
    parser.parse()
    syntax_errors = parser.errors
    semantic_errors = SemanticAnalyzer(parser.statements).analyze()
    return tokens, lexical_errors + syntax_errors + semantic_errors

def main():
    cli = argparse.ArgumentParser(description="Compiler-based C subset error detector")
    cli.add_argument("file", nargs="?", default="input.c", help="C source file (default: input.c)")
    cli.add_argument("--tokens", action="store_true", help="also print tokens")
    args = cli.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}")
        raise SystemExit(2)

    source = path.read_text(encoding="utf-8")
    tokens, errors = analyze(source)
    if args.tokens:
        print("TOKENS")
        for token in tokens:
            print(f"  {token.kind:<12} {token.value!r:<18} line {token.line}")
        print()
    print_report(errors)
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()
