#!/usr/bin/env python3
"""Gate for the lesson bank.

Runs every reference solution against its own checks and rejects anything weak.
Exit code is non-zero on any failure, and build.py refuses to run after one.

    .venv/bin/python tools/validate.py            # whole bank
    .venv/bin/python tools/validate.py stats.py   # one module (ids still checked globally by build)
"""

import re
import signal
import sys

import lib
from lib import runner

TIME_LIMIT = 30
IDENT = re.compile(r"^[a-z][a-z0-9_]*$")
REQUIRED = ["id", "title", "difficulty", "goal", "teach", "starter", "solution", "hints", "explainer", "checks"]
BANNED = re.compile(r"\b(oops|uh oh|simply|easy|obviously|awesome|great job)\b|!(?!\s*=)", re.I)
BANNED_WHERE = ["goal", "explainer"]


class Timeout(Exception):
    pass


def _alarm(_sig, _frame):
    raise Timeout()


def limited(fn, *args):
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TIME_LIMIT)
    try:
        return fn(*args)
    finally:
        signal.alarm(0)


def prose(lesson):
    parts = [lesson.get(k, "") for k in BANNED_WHERE] + list(lesson.get("hints", []))
    parts += [b["text"] for b in lesson.get("teach", []) if b["t"] == "p"]
    return parts


def structure(lesson, seen):
    errors = []
    for field in REQUIRED:
        if field not in lesson:
            errors.append(f"missing field '{field}'")
    if errors:
        return errors
    if not IDENT.match(lesson["id"]):
        errors.append("id must be snake_case")
    if lesson["id"] in seen:
        errors.append(f"duplicate id (also in {seen[lesson['id']]})")
    if len(lesson["hints"]) != 2:
        errors.append("needs exactly 2 hints")
    if not 1 <= lesson["difficulty"] <= 5:
        errors.append("difficulty must be 1-5")
    if len(lesson["checks"]) < 3:
        errors.append("needs >= 3 checks")
    for text in prose(lesson):
        match = BANNED.search(text)
        if match:
            errors.append(f"voice guide: avoid '{match.group(0)}' in: {text[:50]}...")
    if lesson.get("kind") != "text":
        if "function" not in lesson:
            errors.append("code lessons need 'function'")
        for field in ("starter", "solution"):
            try:
                compile(lesson[field], field, "exec")
            except SyntaxError as exc:
                errors.append(f"{field} does not parse: {exc}")
        for i, check in enumerate(lesson["checks"]):
            if "code" not in check or "label" not in check:
                errors.append(f"check[{i}] needs label and code")
    return errors


def behavior(lesson, datasets):
    """Solution passes, starter fails, a wrong stub fails, pitfalls stay quiet."""
    errors = lib.resolve_expected(lesson, datasets)
    if errors:
        return errors

    result = limited(runner.run_lesson, lesson, lesson["solution"], datasets)
    if not result.get("passed"):
        bad = [c["label"] for c in result.get("checks", []) if not c["passed"]]
        return [f"reference solution fails its own checks: {bad or result.get('message')}"]
    fired = runner.pitfall_notes(lesson, lesson["solution"])
    if fired:
        errors.append(f"a pitfall hint fires on the correct solution: {fired}")

    if lesson.get("kind") == "text":
        empty = runner.run_lesson(lesson, "", datasets)
        if empty["passed"]:
            errors.append("an empty answer passes the text checks")
        return errors

    starter = limited(runner.run_lesson, lesson, lesson["starter"], datasets)
    if starter.get("passed"):
        errors.append("the starter code already passes every check")

    wrong = f"def {lesson['function']}(*a, **k):\n    return 0\n"
    control = limited(runner.run_lesson, lesson, wrong, datasets)
    if control.get("passed"):
        errors.append("negative control: a function that always returns 0 passes every check")
    wrong_none = f"def {lesson['function']}(*a, **k):\n    print('x')\n"
    if limited(runner.run_lesson, lesson, wrong_none, datasets).get("passed"):
        errors.append("negative control: a function that only prints passes every check")
    return errors


def validate(only=None):
    datasets = lib.load_datasets()
    lessons = lib.load_lessons(only)
    seen, failed, resolved = {}, 0, []
    for lesson in lessons:
        errors = structure(lesson, seen)
        if not errors:
            try:
                errors = behavior(lesson, datasets)
            except Timeout:
                errors = [f"took longer than {TIME_LIMIT}s"]
        seen[lesson["id"]] = lesson["module"]
        if errors:
            failed += 1
            print(f"FAIL {lesson['id']}  ({lesson['module']})")
            for err in errors:
                print(f"     - {err}")
        else:
            resolved.append(lesson)
    print()
    print("=" * 52)
    print(f"lessons: {len(lessons)}   passed: {len(lessons) - failed}   failed: {failed}")
    print("=" * 52)
    return failed, resolved


if __name__ == "__main__":
    n_failed, _ = validate(sys.argv[1] if len(sys.argv) > 1 else None)
    sys.exit(1 if n_failed else 0)
