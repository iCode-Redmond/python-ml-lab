"""Shared loading for validate.py and build.py."""

import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))

import runner  # noqa: E402


def load_course():
    return json.loads((ROOT / "data" / "course.json").read_text())


def load_datasets():
    return {p.stem: p.read_text() for p in sorted((ROOT / "data" / "datasets").glob("*.csv"))}


def load_lessons(only=None):
    """Lessons in course order. Each lesson dict gets its module id."""
    course = load_course()
    lessons = []
    for mod in course["modules"]:
        path = ROOT / "data" / "lessons" / f"{mod['id']}.py"
        if only and path.name != only:
            continue
        spec = importlib.util.spec_from_file_location(f"lessons_{mod['id']}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for lesson in module.LESSONS:
            lesson = json.loads(json.dumps(lesson))  # detach, ensure JSON-native
            lesson["module"] = mod["id"]
            lessons.append(lesson)
    return lessons


def resolve_expected(lesson, datasets):
    """Fill every check's `expected` by running the reference solution.

    A hand-pinned `expected` is kept and compared later by validate.py. Returns
    a list of problems (empty when the solution ran cleanly).
    """
    if lesson.get("kind") == "text":
        return []
    ns = runner.build_namespace(lesson, datasets)
    problems = []
    try:
        exec(compile(lesson["solution"], "<solution>", "exec"), ns)
    except Exception as exc:  # noqa: BLE001
        return [f"solution failed to run: {type(exc).__name__}: {exc}"]
    for check in lesson["checks"]:
        scope = runner.build_namespace(lesson, datasets)
        scope.update({k: v for k, v in ns.items() if not k.startswith("__")})
        try:
            exec(compile(check["code"], "<check>", "exec"), scope)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"check '{check['label']}' raised {type(exc).__name__}: {exc}")
            continue
        actual = runner.to_native(scope.get("result"))
        if "expected" in check:
            check["pinned"] = True
            if not runner.same(actual, check["expected"], check.get("tol", 1e-6)):
                problems.append(
                    f"check '{check['label']}': solution gives {actual!r}, pinned expected {check['expected']!r}"
                )
        else:
            check["expected"] = actual
    return problems
