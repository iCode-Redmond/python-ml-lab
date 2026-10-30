MODULE = "logistic"

SETUP = '''SIZES = [3.78, 2.44, 2.09, 0.14, 1.72, 1.65, 4.92, 4.37, 4.96, 4.52, 3.69, 5.88]
LABELS = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
'''

LESSONS = [
    {
        "id": "classify_tumor", "title": "Classify a tumor", "difficulty": 3, "minutes": 12,
        "goal": "Train a logistic regression on tumor sizes and return 0 (benign) or 1 (malignant).",
        "setup": SETUP,
        "teach": [
            {"t": "p", "text": "Logistic regression predicts a category. The lists `SIZES` and `LABELS` are provided: each tumor size in centimetres, and whether it was malignant (1) or not (0)."},
            {"t": "code", "text": "import numpy as np\nX = np.array(SIZES).reshape(-1, 1)   # scikit-learn wants a 2D table\nprint(X.shape)   # (12, 1)"},
            {"t": "p", "text": "`reshape(-1, 1)` turns a flat list into one column. Fit a `LogisticRegression` on it, then predict for a new size."},
        ],
        "function": "classify_tumor",
        "starter": "import numpy as np\nfrom sklearn.linear_model import LogisticRegression\n\ndef classify_tumor(size):\n    # return 0 or 1 for a tumor of this size\n    pass\n",
        "solution": "import numpy as np\nfrom sklearn.linear_model import LogisticRegression\n\ndef classify_tumor(size):\n    X = np.array(SIZES).reshape(-1, 1)\n    model = LogisticRegression().fit(X, LABELS)\n    return int(model.predict([[size]])[0])\n",
        "hints": [
            "Reshape `SIZES` into a single column, then call `LogisticRegression().fit(X, LABELS)`.",
            "`model.predict([[size]])` returns an array. Take element `[0]` and wrap it in `int(...)`.",
        ],
        "explainer": "The model learns a boundary size. Sizes below it predict 0 and sizes above it predict 1.",
        "checks": [
            {"label": "3.46 is benign", "code": "result = classify_tumor(3.46)", "expected": 0},
            {"label": "4.80 is malignant", "code": "result = classify_tumor(4.80)", "expected": 1},
            {"label": "a tiny tumor", "code": "result = classify_tumor(0.5)", "expected": 0},
            {"label": "a large tumor", "code": "result = classify_tumor(6.5)", "expected": 1},
            {"label": "returns a plain int", "code": "result = type(classify_tumor(4.0)).__name__", "expected": "int"},
        ],
        "pitfalls": [{"missing": r"reshape", "say": "scikit-learn expects a 2D table. Reshape the flat list with `.reshape(-1, 1)`."}],
    },
    {
        "id": "tumor_probability", "title": "Read the probability", "difficulty": 3, "minutes": 10,
        "goal": "Return the model's probability that a tumor of a given size is malignant.",
        "setup": SETUP,
        "teach": [
            {"t": "p", "text": "A classifier also knows how sure it is. `predict_proba` returns one row per input with a probability for each class: first class 0, then class 1."},
            {"t": "code", "text": "p = model.predict_proba([[4.0]])\nprint(p)   # [[0.3 0.7]]  (class 0, class 1)"},
            {"t": "p", "text": "Return the probability of class 1 as a float."},
        ],
        "function": "tumor_probability",
        "starter": "import numpy as np\nfrom sklearn.linear_model import LogisticRegression\n\ndef tumor_probability(size):\n    # probability the tumor is malignant\n    pass\n",
        "solution": "import numpy as np\nfrom sklearn.linear_model import LogisticRegression\n\ndef tumor_probability(size):\n    X = np.array(SIZES).reshape(-1, 1)\n    model = LogisticRegression().fit(X, LABELS)\n    return float(model.predict_proba([[size]])[0][1])\n",
        "hints": [
            "Train as in the last lesson, but call `predict_proba` instead of `predict`.",
            "The result is a table with one row. Row `[0]`, column `[1]` is the class 1 probability.",
        ],
        "explainer": "`predict` applies a 0.5 cut-off to this probability. Reading the probability directly shows how close to the boundary a case is.",
        "checks": [
            {"label": "3.46", "code": "result = tumor_probability(3.46)", "tol": 1e-3},
            {"label": "4.80", "code": "result = tumor_probability(4.80)", "tol": 1e-3},
            {"label": "larger tumors are more likely malignant", "code": "result = tumor_probability(6.0) > tumor_probability(2.0)", "expected": True},
            {"label": "a probability is between 0 and 1", "code": "p = tumor_probability(4.0)\nresult = 0 <= p <= 1", "expected": True},
        ],
    },
]
