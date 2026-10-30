#!/usr/bin/env python3
"""Behavior tests for engine/runner.py (CPython).

    .venv/bin/python tools/test_runner.py
"""

import sys
import unittest

import lib
from lib import runner

DATA = lib.load_datasets()
LESSONS = {l["id"]: l for l in lib.load_lessons()}
for _lesson in LESSONS.values():
    lib.resolve_expected(_lesson, DATA)


def run(lesson_id, code):
    return runner.run_only(LESSONS[lesson_id], code, DATA)


def check(lesson_id, code):
    return runner.run_lesson(LESSONS[lesson_id], code, DATA)


class RunTests(unittest.TestCase):
    def test_function_only_code_calls_the_sample(self):
        r = run("mean_of", "def mean_of(nums):\n    return sum(nums) / len(nums)\n")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["call"], "mean_of([2, 4, 6])")
        self.assertEqual(r["value"], "4.0")

    def test_print_inside_function_is_shown(self):
        code = "def test_mae(df):\n    print(df.head(3))\n    return df\n"
        r = run("test_mae", code)
        self.assertIn("Toyoty", r["stdout"])
        self.assertEqual(r["call"], "test_mae(co2)")

    def test_dataset_is_available_at_module_level(self):
        r = run("test_mae", "print(len(co2))\n")
        self.assertEqual(r["stdout"].strip(), "33")
        self.assertIsNone(r["call"])

    def test_returned_table_is_shown_as_a_table(self):
        r = run("test_mae", "def test_mae(df):\n    return df\n")
        self.assertIn("Volume", r["value"])
        self.assertNotIn("{'Car'", r["value"])

    def test_no_function_defined_means_no_call(self):
        r = run("mean_of", "x = 1\n")
        self.assertIsNone(r["call"])
        self.assertEqual(r["stdout"], "")

    def test_error_inside_function_reports_the_line(self):
        code = "def mean_of(nums):\n    total = 0\n    return total / 0\n"
        r = run("mean_of", code)
        self.assertEqual(r["status"], "error")
        self.assertEqual(r["error"]["type"], "ZeroDivisionError")
        self.assertEqual(r["error"]["line"], 3)
        self.assertIn("line 3", r["message"])

    def test_syntax_error_is_explained(self):
        r = run("mean_of", "def mean_of(nums)\n    return 1\n")
        self.assertEqual(r["error"]["type"], "SyntaxError")
        self.assertIn("cannot read", r["message"])

    def test_printed_output_survives_an_error(self):
        code = "def mean_of(nums):\n    print('start')\n    return nums[99]\n"
        r = run("mean_of", code)
        self.assertEqual(r["status"], "error")
        self.assertIn("start", r["stdout"])

    def test_every_lesson_has_a_sample_call(self):
        for lesson in LESSONS.values():
            if lesson.get("kind") != "text":
                self.assertTrue(runner.sample_call(lesson), lesson["id"])

    def test_every_sample_call_runs_on_the_reference_solution(self):
        for lesson in LESSONS.values():
            if lesson.get("kind") == "text":
                continue
            r = runner.run_only(lesson, lesson["solution"], DATA)
            self.assertEqual(r["status"], "ok", f"{lesson['id']}: {r.get('message')}")
            self.assertIsNotNone(r["value"], lesson["id"])


class CheckTests(unittest.TestCase):
    def test_infinite_loop_guard_is_not_the_runner_job(self):
        # The page kills the worker after 10 s. The runner itself has no timer.
        self.assertTrue(hasattr(runner, "run_lesson"))

    def test_missing_definition_is_named(self):
        r = check("mean_of", "x = 1\n")
        self.assertEqual(r["status"], "error")
        self.assertIn("mean_of", r["message"])

    def test_printing_instead_of_returning_is_diagnosed(self):
        r = check("mean_of", "def mean_of(nums):\n    print(sum(nums) / len(nums))\n")
        self.assertFalse(r["passed"])
        self.assertIn("did not return", r["checks"][0]["note"])

    def test_checks_see_clean_data_even_if_the_code_edits_it(self):
        code = "co2.drop(co2.index, inplace=True)\ndef split_sizes(df):\n    return 0, 0\n"
        r = check("split_sizes", code)
        self.assertFalse(r["passed"])
        self.assertIn("actual", r["checks"][0])

    def test_text_lesson_rejects_empty_and_accepts_a_real_answer(self):
        self.assertFalse(check("reflection", "")["passed"])
        self.assertTrue(check("reflection", LESSONS["reflection"]["solution"])["passed"])

    def test_wrong_value_is_reported_with_expected_and_actual(self):
        r = check("mean_of", "def mean_of(nums):\n    return 0\n")
        first = r["checks"][0]
        self.assertEqual((first["expected"], first["actual"]), ("4.0", "0"))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], "-v"] if len(sys.argv) == 1 else sys.argv)
