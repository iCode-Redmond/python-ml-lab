#!/usr/bin/env python3
"""Try to fool the gate. Every fixture here is a broken lesson the validator must reject.

    .venv/bin/python tools/test_validate.py
"""

import copy
import sys

import validate

BASE = {
    "id": "double_it", "module": "fixture", "title": "Double", "difficulty": 1, "minutes": 5,
    "goal": "Return twice the number.",
    "teach": [{"t": "p", "text": "Multiply by 2."}],
    "function": "double_it",
    "starter": "def double_it(n):\n    pass\n",
    "solution": "def double_it(n):\n    return n * 2\n",
    "hints": ["Multiply.", "Use the * operator."],
    "explainer": "Multiplying by two doubles it.",
    "checks": [
        {"label": "2", "code": "result = double_it(2)"},
        {"label": "3", "code": "result = double_it(3)"},
        {"label": "-1", "code": "result = double_it(-1)"},
    ],
}


def broken(**changes):
    lesson = copy.deepcopy(BASE)
    lesson.update(changes)
    return lesson


FIXTURES = {
    "good lesson passes": (BASE, True),
    "solution disagrees with a pinned value": (broken(checks=[
        {"label": "a", "code": "result = double_it(2)", "expected": 5},
        {"label": "b", "code": "result = double_it(3)"}, {"label": "c", "code": "result = double_it(4)"}]), False),
    "starter already passes": (broken(starter="def double_it(n):\n    return n * 2\n"), False),
    "checks so weak a constant passes": (broken(checks=[
        {"label": "a", "code": "result = double_it(0)"}, {"label": "b", "code": "result = double_it(0.0)"},
        {"label": "c", "code": "result = double_it(-0)"}]), False),
    "only one hint": (broken(hints=["Multiply."]), False),
    "too few checks": (broken(checks=BASE["checks"][:2]), False),
    "banned voice word": (broken(goal="Oops, this is easy!"), False),
    "pitfall fires on the solution": (broken(pitfalls=[{"found": r"return", "say": "x"}]), False),
    "solution crashes": (broken(solution="def double_it(n):\n    return n / 0\n"), False),
    "missing function name": (broken(function="nope"), False),
}


def main():
    bad = 0
    for name, (lesson, should_pass) in FIXTURES.items():
        errors = validate.structure(lesson, {})
        if not errors:
            try:
                errors = validate.behavior(lesson, {})
            except Exception as exc:  # noqa: BLE001
                errors = [f"raised {type(exc).__name__}"]
        passed = not errors
        ok = passed == should_pass
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f"   gate said: {errors or 'pass'}"))
    print(f"\n{len(FIXTURES) - bad} of {len(FIXTURES)} fixtures behave")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
