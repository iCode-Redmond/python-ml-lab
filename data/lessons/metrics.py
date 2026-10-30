MODULE = "metrics"
LESSONS = [
    {
        "id": "confusion_counts", "title": "Confusion counts", "difficulty": 2, "minutes": 10,
        "goal": "Count true positives, false positives, true negatives and false negatives.",
        "teach": [
            {"t": "p", "text": "A classifier predicts 1 (positive) or 0 (negative). Each prediction is one of four outcomes. True positive: predicted 1, actually 1. False positive: predicted 1, actually 0. True negative: predicted 0, actually 0. False negative: predicted 0, actually 1."},
            {"t": "code", "text": "actual    = [1, 0, 1, 0]\npredicted = [1, 1, 0, 0]\n# pair 1: tp, pair 2: fp, pair 3: fn, pair 4: tn"},
            {"t": "p", "text": "Return a dictionary with the keys `tp`, `fp`, `tn`, `fn`."},
        ],
        "function": "confusion_counts",
        "starter": "def confusion_counts(actual, predicted):\n    # return {'tp': ..., 'fp': ..., 'tn': ..., 'fn': ...}\n    pass\n",
        "solution": "def confusion_counts(actual, predicted):\n    counts = {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0}\n    for a, p in zip(actual, predicted):\n        if p == 1 and a == 1:\n            counts['tp'] += 1\n        elif p == 1 and a == 0:\n            counts['fp'] += 1\n        elif p == 0 and a == 0:\n            counts['tn'] += 1\n        else:\n            counts['fn'] += 1\n    return counts\n",
        "hints": [
            "Walk both lists together with `zip(actual, predicted)` and look at each pair.",
            "Start a dictionary with all four keys at 0 and add 1 to the key that matches the pair.",
        ],
        "explainer": "Every pair falls into exactly one of the four cases, so the four counts add up to the number of predictions.",
        "checks": [
            {"label": "one of each outcome", "code": "result = confusion_counts([1, 0, 1, 0], [1, 1, 0, 0])"},
            {"label": "perfect predictions", "code": "result = confusion_counts([1, 1, 0], [1, 1, 0])"},
            {"label": "always predicts 1", "code": "result = confusion_counts([1, 0, 0, 1], [1, 1, 1, 1])"},
            {"label": "empty lists", "code": "result = confusion_counts([], [])"},
            {"label": "mixed", "code": "result = confusion_counts([1, 1, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0])"},
        ],
    },
    {
        "id": "accuracy_of", "title": "Accuracy", "difficulty": 1, "minutes": 5,
        "goal": "Return the fraction of predictions that were correct.",
        "teach": [
            {"t": "p", "text": "Accuracy is correct predictions divided by all predictions. Correct means true positives plus true negatives."},
            {"t": "code", "text": "# tp=3, fp=1, tn=4, fn=2\n# correct = 3 + 4 = 7, total = 10, accuracy = 0.7"},
            {"t": "p", "text": "Return 0.0 when there are no predictions at all."},
        ],
        "function": "accuracy_of",
        "starter": "def accuracy_of(tp, fp, tn, fn):\n    # fraction of predictions that were correct\n    pass\n",
        "solution": "def accuracy_of(tp, fp, tn, fn):\n    total = tp + fp + tn + fn\n    if total == 0:\n        return 0.0\n    return (tp + tn) / total\n",
        "hints": [
            "Add all four counts to get the total. The numerator uses only two of them.",
            "Check `total == 0` before dividing.",
        ],
        "explainer": "True positives and true negatives are the correct cases. The guard stops the division when no predictions were made.",
        "checks": [
            {"label": "tp=3 fp=1 tn=4 fn=2", "code": "result = accuracy_of(3, 1, 4, 2)", "expected": 0.7},
            {"label": "all correct", "code": "result = accuracy_of(5, 0, 5, 0)", "expected": 1.0},
            {"label": "all wrong", "code": "result = accuracy_of(0, 4, 0, 4)", "expected": 0.0},
            {"label": "no predictions", "code": "result = accuracy_of(0, 0, 0, 0)", "expected": 0.0},
        ],
    },
    {
        "id": "precision_recall", "title": "Precision and recall", "difficulty": 3, "minutes": 10,
        "goal": "Return (precision, recall) from the counts.",
        "teach": [
            {"t": "p", "text": "Precision asks: of everything predicted positive, how much was truly positive? It is tp / (tp + fp). Recall asks: of everything truly positive, how much did the model find? It is tp / (tp + fn)."},
            {"t": "code", "text": "# tp=6, fp=2, fn=3\n# precision = 6 / 8 = 0.75\n# recall    = 6 / 9 = 0.666..."},
            {"t": "p", "text": "When a denominator is 0, return 0.0 for that value."},
        ],
        "function": "precision_recall",
        "starter": "def precision_recall(tp, fp, fn):\n    # return (precision, recall)\n    pass\n",
        "solution": "def precision_recall(tp, fp, fn):\n    precision = tp / (tp + fp) if tp + fp else 0.0\n    recall = tp / (tp + fn) if tp + fn else 0.0\n    return precision, recall\n",
        "hints": [
            "Write each ratio on its own line. They share the numerator `tp` but not the denominator.",
            "Guard each denominator separately, because one can be 0 while the other is not.",
        ],
        "explainer": "Precision punishes false positives and recall punishes false negatives. The guards make an empty denominator mean 0.0 instead of an error.",
        "checks": [
            {"label": "tp=6 fp=2 fn=3", "code": "result = list(precision_recall(6, 2, 3))"},
            {"label": "perfect", "code": "result = list(precision_recall(5, 0, 0))", "expected": [1.0, 1.0]},
            {"label": "no positive predictions", "code": "result = list(precision_recall(0, 0, 4))", "expected": [0.0, 0.0]},
            {"label": "no real positives", "code": "result = list(precision_recall(0, 3, 0))", "expected": [0.0, 0.0]},
        ],
    },
    {
        "id": "f1_of", "title": "F1 score", "difficulty": 2, "minutes": 6,
        "goal": "Return the F1 score, the harmonic mean of precision and recall.",
        "teach": [
            {"t": "p", "text": "F1 combines precision and recall in one number: `2 * p * r / (p + r)`. It is high only when both are high."},
            {"t": "code", "text": "p, r = 0.75, 0.6\nprint(2 * p * r / (p + r))   # 0.666..."},
            {"t": "p", "text": "Return 0.0 when `p + r` is 0."},
        ],
        "function": "f1_of",
        "starter": "def f1_of(precision, recall):\n    # harmonic mean of precision and recall\n    pass\n",
        "solution": "def f1_of(precision, recall):\n    if precision + recall == 0:\n        return 0.0\n    return 2 * precision * recall / (precision + recall)\n",
        "hints": [
            "Use the formula `2 * p * r / (p + r)` directly.",
            "Return early when `precision + recall` is 0.",
        ],
        "explainer": "The harmonic mean is pulled toward the smaller of the two values, so a model cannot hide poor recall behind great precision.",
        "checks": [
            {"label": "0.75 and 0.6", "code": "result = f1_of(0.75, 0.6)"},
            {"label": "equal values", "code": "result = f1_of(0.5, 0.5)", "expected": 0.5},
            {"label": "one value is zero", "code": "result = f1_of(1.0, 0.0)", "expected": 0.0},
            {"label": "both zero", "code": "result = f1_of(0.0, 0.0)", "expected": 0.0},
        ],
    },
]
