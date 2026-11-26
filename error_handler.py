def make_error(phase, token, message, suggestion):
    return {
        "phase": phase,
        "line": getattr(token, "line", 1),
        "column": getattr(token, "column", 1),
        "message": message,
        "suggestion": suggestion,
    }

def print_report(errors):
    print("=" * 62)
    print(" SMART PROGRAMMING ERROR DETECTOR")
    print("=" * 62)
    if not errors:
        print("No errors detected in the supported C subset.")
        print("Note: this is an educational analyzer, not a full C compiler.")
        return
    print(f"Found {len(errors)} issue(s):\n")
    for i, err in enumerate(errors, 1):
        print(f"{i}. [{err['phase']} Error] Line {err['line']}, Column {err['column']}")
        print(f"   Meaning : {err['message']}")
        print(f"   Suggest : {err['suggestion']}")
        print()
    print("Note: this analyzer supports only a small educational subset of C.")
