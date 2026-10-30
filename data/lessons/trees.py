MODULE = "trees"
LESSONS = [
    {
        "id": "encode_go", "title": "Encode categories", "difficulty": 2, "minutes": 10,
        "goal": "Return a copy of the table where Nationality and Go are numbers.",
        "datasets": ["decision"],
        "teach": [
            {"t": "p", "text": "Decision trees in scikit-learn need numbers. The `decision` table has text in two columns: Nationality (UK, USA, N) and Go (YES, NO). A dictionary maps each text value to a number, and `Series.map` applies it to a column."},
            {"t": "code", "text": "codes = {'UK': 0, 'USA': 1, 'N': 2}\nout = df.copy()\nout['Nationality'] = out['Nationality'].map(codes)"},
            {"t": "p", "text": "Map Nationality as UK 0, USA 1, N 2, and Go as NO 0, YES 1. Work on a copy so the caller's table stays unchanged."},
        ],
        "function": "encode_go",
        "starter": "def encode_go(df):\n    # return a new DataFrame with numeric Nationality and Go\n    pass\n",
        "solution": "def encode_go(df):\n    out = df.copy()\n    out['Nationality'] = out['Nationality'].map({'UK': 0, 'USA': 1, 'N': 2})\n    out['Go'] = out['Go'].map({'NO': 0, 'YES': 1})\n    return out\n",
        "hints": [
            "Start from `df.copy()`, then replace each text column with `column.map(dictionary)`.",
            "Return the new table. Check that `Nationality` uses UK 0, USA 1, N 2.",
        ],
        "explainer": "`map` swaps each text value for its number. Copying first means the original table is not changed behind the caller's back.",
        "checks": [
            {"label": "Nationality becomes numbers", "code": "result = list(encode_go(decision)['Nationality'])"},
            {"label": "Go becomes 0 and 1", "code": "result = list(encode_go(decision)['Go'])"},
            {"label": "Age is untouched", "code": "result = list(encode_go(decision)['Age'])"},
            {"label": "the original table is unchanged", "code": "before = list(decision['Go'])\nencode_go(decision)\nresult = list(decision['Go']) == before", "expected": True},
        ],
    },
    {
        "id": "train_tree", "title": "Train a tree", "difficulty": 3, "minutes": 12,
        "goal": "Train a decision tree on the encoded table and return it.",
        "datasets": ["decision"],
        "setup": "def prepare(df):\n    out = df.copy()\n    out['Nationality'] = out['Nationality'].map({'UK': 0, 'USA': 1, 'N': 2})\n    out['Go'] = out['Go'].map({'NO': 0, 'YES': 1})\n    return out\n",
        "teach": [
            {"t": "p", "text": "A decision tree learns a series of yes/no questions about the inputs. It is trained with `fit(inputs, target)`. The helper `prepare(df)` is provided and returns the encoded table from the last lesson."},
            {"t": "code", "text": "from sklearn.tree import DecisionTreeClassifier\ntree = DecisionTreeClassifier(random_state=0)\ntree.fit(inputs, target)"},
            {"t": "p", "text": "The inputs are Age, Experience, Rank and Nationality. The target is Go. Set `random_state=0` so training is repeatable."},
        ],
        "function": "train_tree",
        "starter": "from sklearn.tree import DecisionTreeClassifier\n\ndef train_tree(df):\n    # return a trained DecisionTreeClassifier\n    pass\n",
        "solution": "from sklearn.tree import DecisionTreeClassifier\n\ndef train_tree(df):\n    data = prepare(df)\n    cols = ['Age', 'Experience', 'Rank', 'Nationality']\n    tree = DecisionTreeClassifier(random_state=0)\n    tree.fit(data[cols], data['Go'])\n    return tree\n",
        "hints": [
            "Call `prepare(df)` first, then choose the four input columns as one list.",
            "Fit with `tree.fit(data[cols], data['Go'])` and return `tree`, not the result of `fit`'s printout.",
        ],
        "explainer": "The tree splits the rows on questions like \"Rank at most 6.5\" until each group is pure. It returns the trained object so the caller can predict with it.",
        "checks": [
            {"label": "returns a trained tree", "code": "t = train_tree(decision)\nresult = hasattr(t, 'tree_')", "expected": True},
            {"label": "it fits every training row", "code": "import pandas as pd\nd = prepare(decision)\nt = train_tree(decision)\nresult = float(t.score(d[['Age','Experience','Rank','Nationality']], d['Go']))", "expected": 1.0},
            {"label": "predicts for a new candidate", "code": "import pandas as pd\nt = train_tree(decision)\nrow = pd.DataFrame([[40, 10, 7, 1]], columns=['Age','Experience','Rank','Nationality'])\nresult = t.predict(row).tolist()"},
        ],
        "pitfalls": [{"missing": r"\.fit\(", "say": "The tree is never trained. Call `tree.fit(inputs, target)`."}],
    },
]
