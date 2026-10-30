"""Lesson runner. One file, two hosts.

The same code grades a submission in the browser (Pyodide, inside a
Web Worker) and grades the reference solutions in CPython (tools/validate.py).
If it passes in one and fails in the other, the bug is in the lesson, not here.

Public entry point: run_lesson(lesson, code, datasets) -> dict
"""

import contextlib
import io
import math
import re
import traceback

USER_FILE = "<user>"


# ---------------------------------------------------------------- values ----

def to_native(value):
    """Turn numpy / pandas values into plain JSON-style Python values."""
    mod = type(value).__module__
    if mod.startswith("numpy"):
        if hasattr(value, "tolist"):
            return to_native(value.tolist())
    if mod.startswith("pandas"):
        if hasattr(value, "to_dict") and hasattr(value, "columns"):
            return to_native(value.to_dict(orient="list"))
        if hasattr(value, "tolist"):
            return to_native(value.tolist())
    if isinstance(value, dict):
        return {str(k): to_native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_native(v) for v in value]
    return value


def same(actual, expected, tol=1e-6):
    """Equality with float tolerance. bool is never equal to 0/1."""
    if isinstance(expected, bool) or isinstance(actual, bool):
        return isinstance(actual, bool) and isinstance(expected, bool) and actual == expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if isinstance(actual, float) and math.isnan(actual):
            return False
        return math.isclose(actual, expected, rel_tol=tol, abs_tol=tol)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(expected) == len(actual) and all(
            same(a, e, tol) for a, e in zip(actual, expected)
        )
    if isinstance(expected, dict) and isinstance(actual, dict):
        return expected.keys() == actual.keys() and all(
            same(actual[k], expected[k], tol) for k in expected
        )
    return actual == expected


def show(value, limit=160):
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


# ------------------------------------------------------------- execution ----

def build_namespace(lesson, datasets):
    """A fresh namespace: datasets as DataFrames, then the hidden setup code."""
    ns = {"__name__": "user"}
    names = lesson.get("datasets", [])
    if names:
        import io as _io

        import pandas as pd

        for name in names:
            ns[name] = pd.read_csv(_io.StringIO(datasets[name]))
    if lesson.get("setup"):
        exec(compile(lesson["setup"], "<setup>", "exec"), ns)
    return ns


def user_line(exc):
    """Line number inside the submitted code where an exception surfaced."""
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == USER_FILE:
            line = frame.lineno
    return line


def describe_error(exc):
    return {"type": type(exc).__name__, "message": str(exc), "line": user_line(exc)}


def friendly_error(err):
    """Say what happened, where, and what to try. No jokes."""
    where = f" on line {err['line']}" if err["line"] else ""
    name, msg = err["type"], err["message"]
    if name == "SyntaxError":
        return f"Python cannot read this code{where}. Check for a missing colon, bracket or quote. {msg}"
    if name == "IndentationError":
        return f"The spacing at the start of a line is wrong{where}. Lines inside a function need the same indent. {msg}"
    if name == "NameError":
        return f"{msg}{where}. Check the spelling, and that you defined it before using it."
    if name == "TypeError":
        return f"{msg}{where}. A value has a different type than the code expects."
    if name == "KeyError":
        return f"The key {msg} is not there{where}. Check the spelling of the name or column."
    if name == "IndexError":
        return f"{msg}{where}. The list is shorter than the position you asked for."
    if name == "ZeroDivisionError":
        return f"The code divided by zero{where}. Check what you divide by when the input is empty."
    if name == "NotFittedError":
        return f"The model was used before it was trained{where}. Call fit() first."
    return f"{name}{where}: {msg}"


# ----------------------------------------------------------- diagnostics ----

def diagnose(actual, expected, stdout):
    """Plain-language reason a value is wrong. Heuristic, never an LLM."""
    if actual is None and expected is not None:
        if stdout.strip():
            return (
                "The function printed something but did not return it. "
                "print shows a value on screen. return hands it back to the code that called the function."
            )
        return "The function returned None. Add a return statement that gives back the answer."
    if isinstance(actual, float) and math.isnan(actual):
        return "The result is NaN, which means a calculation had no valid input. Check for an empty list or a division by zero."
    exp_num = isinstance(expected, (int, float)) and not isinstance(expected, bool)
    act_num = isinstance(actual, (int, float)) and not isinstance(actual, bool)
    if exp_num and act_num:
        if abs(actual - expected) == 1:
            return "The answer is off by exactly 1. Check where your range or count starts and stops."
        if expected != 0 and abs(actual - expected) / abs(expected) < 0.02:
            return "The answer is close. Check rounding, or whether you used the right formula variant."
        if actual == -expected:
            return "The sign is flipped. Check the order of the subtraction."
        return None
    if type(actual) is not type(expected):
        return f"Expected a {type(expected).__name__} but got a {type(actual).__name__}."
    if isinstance(expected, list) and isinstance(actual, list) and len(expected) != len(actual):
        return f"Expected {len(expected)} items but got {len(actual)}."
    if isinstance(expected, str) and isinstance(actual, str) and expected.lower() == actual.lower():
        return "The text matches except for capital letters."
    return None


def pitfall_notes(lesson, code):
    notes = []
    for rule in lesson.get("pitfalls", []):
        if "missing" in rule and not re.search(rule["missing"], code):
            notes.append(rule["say"])
        if "found" in rule and re.search(rule["found"], code):
            notes.append(rule["say"])
    return notes


# ------------------------------------------------------------- text kind ----

def run_text_lesson(lesson, text):
    results = []
    words = re.findall(r"[A-Za-z']+", text)
    lowered = text.lower()
    for check in lesson["checks"]:
        if "min_words" in check:
            ok = len(words) >= check["min_words"]
            note = None if ok else f"Write at least {check['min_words']} words. You have {len(words)}."
        else:
            ok = any(k.lower() in lowered for k in check["any_of"])
            note = None if ok else check.get("say")
        results.append({"label": check["label"], "passed": ok, "note": note})
    return {"status": "ok", "stdout": "", "checks": results, "passed": all(r["passed"] for r in results)}


# ------------------------------------------------------------- main entry ---

def run_lesson(lesson, code, datasets=None):
    datasets = datasets or {}
    if lesson.get("kind") == "text":
        return run_text_lesson(lesson, code)

    out = io.StringIO()
    result = {"status": "ok", "stdout": "", "checks": [], "passed": False, "error": None, "notes": []}

    try:
        ns = build_namespace(lesson, datasets)
        with contextlib.redirect_stdout(out):
            exec(compile(code, USER_FILE, "exec"), ns)
    except BaseException as exc:  # noqa: BLE001 - SystemExit from exit() too
        err = describe_error(exc)
        result.update(status="error", error=err, message=friendly_error(err), stdout=out.getvalue())
        return result

    result["stdout"] = out.getvalue()
    target = lesson.get("function")
    if target and not callable(ns.get(target)):
        result.update(
            status="error",
            error={"type": "MissingDefinition", "message": target, "line": None},
            message=f"The code does not define {target}. Keep the name exactly as it appears in the starter code.",
        )
        return result

    for check in lesson["checks"]:
        scope = build_namespace(lesson, datasets)
        scope.update({k: v for k, v in ns.items() if not k.startswith("__")})
        for name in lesson.get("datasets", []):  # checks always see pristine data
            scope[name] = build_namespace({"datasets": [name]}, datasets)[name]
        entry = {"label": check["label"], "passed": False, "note": None}
        check_out = io.StringIO()
        try:
            with contextlib.redirect_stdout(check_out):
                exec(compile(check["code"], "<check>", "exec"), scope)
            actual = to_native(scope.get("result"))
            expected = check["expected"]
            entry["passed"] = same(actual, expected, check.get("tol", 1e-6))
            if not entry["passed"]:
                entry["actual"] = show(actual)
                entry["expected"] = show(expected)
                entry["note"] = diagnose(actual, expected, check_out.getvalue() or result["stdout"])
        except BaseException as exc:  # noqa: BLE001
            err = describe_error(exc)
            entry["note"] = friendly_error(err)
        result["checks"].append(entry)

    result["passed"] = all(c["passed"] for c in result["checks"])
    if not result["passed"]:
        result["notes"] = pitfall_notes(lesson, code)
    return result


def run_only(lesson, code, datasets=None):
    """Run the code and report what it printed. No grading."""
    out = io.StringIO()
    try:
        ns = build_namespace(lesson, datasets or {})
        with contextlib.redirect_stdout(out):
            exec(compile(code, USER_FILE, "exec"), ns)
    except BaseException as exc:  # noqa: BLE001
        err = describe_error(exc)
        return {"status": "error", "stdout": out.getvalue(), "error": err, "message": friendly_error(err)}
    return {"status": "ok", "stdout": out.getvalue()}
