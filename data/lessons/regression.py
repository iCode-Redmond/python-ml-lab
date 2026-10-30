MODULE = "regression"
LESSONS = [
    {
        "id": "fit_line", "title": "Fit a line by hand", "difficulty": 3, "minutes": 12,
        "goal": "Return (slope, intercept) of the least-squares line through the points.",
        "teach": [
            {"t": "p", "text": "Linear regression finds the line `y = slope * x + intercept` that sits closest to the points. For one input the formulas are: slope = sum((x - mean_x) * (y - mean_y)) / sum((x - mean_x) ** 2), and intercept = mean_y - slope * mean_x."},
            {"t": "code", "text": "xs = [1, 2, 3]\nys = [2, 4, 6]\n# every point lies on y = 2x, so slope = 2 and intercept = 0"},
            {"t": "p", "text": "Return the two numbers as a tuple: `return slope, intercept`."},
        ],
        "function": "fit_line",
        "starter": "def fit_line(xs, ys):\n    # return (slope, intercept)\n    pass\n",
        "solution": "def fit_line(xs, ys):\n    mx = sum(xs) / len(xs)\n    my = sum(ys) / len(ys)\n    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))\n    den = sum((x - mx) ** 2 for x in xs)\n    slope = num / den\n    return slope, my - slope * mx\n",
        "hints": [
            "Compute `mean_x` and `mean_y` first. Both formulas use them.",
            "Use `zip(xs, ys)` to walk the pairs together for the top of the slope formula.",
        ],
        "explainer": "The slope is how much y moves per unit of x, measured against how much x varies. The intercept then makes the line pass through the point (mean_x, mean_y).",
        "checks": [
            {"label": "points on y = 2x", "code": "result = list(fit_line([1, 2, 3], [2, 4, 6]))"},
            {"label": "points on y = x + 1", "code": "result = list(fit_line([0, 1, 2, 3], [1, 2, 3, 4]))"},
            {"label": "a falling line", "code": "result = list(fit_line([0, 2, 4], [10, 6, 2]))"},
            {"label": "noisy points", "code": "result = list(fit_line([1, 2, 3, 4], [2, 3, 5, 4]))"},
        ],
    },
    {
        "id": "split_sizes", "title": "Train and test split", "difficulty": 2, "minutes": 8,
        "goal": "Split the car data and return (train_rows, test_rows).",
        "datasets": ["co2"],
        "teach": [
            {"t": "p", "text": "A model is judged on data it has not seen. `train_test_split` shuffles the rows and sets some aside for testing. The variable `co2` is a pandas DataFrame of cars with columns Car, Model, Volume, Weight and CO2."},
            {"t": "code", "text": "from sklearn.model_selection import train_test_split\ntrain, test = train_test_split(co2, test_size=0.2, random_state=42)\nprint(len(train), len(test))"},
            {"t": "p", "text": "`random_state` fixes the shuffle so the split is the same every run. Write `split_sizes(df)` with `test_size=0.2` and `random_state=42`."},
        ],
        "function": "split_sizes",
        "starter": "from sklearn.model_selection import train_test_split\n\ndef split_sizes(df):\n    # return (number of train rows, number of test rows)\n    pass\n",
        "solution": "from sklearn.model_selection import train_test_split\n\ndef split_sizes(df):\n    train, test = train_test_split(df, test_size=0.2, random_state=42)\n    return len(train), len(test)\n",
        "hints": [
            "`train_test_split` returns two DataFrames when you give it one DataFrame.",
            "Pass `test_size=0.2` and `random_state=42`, then return `len(train), len(test)`.",
        ],
        "explainer": "Twenty percent of 33 rows rounds up to 7 test rows, leaving 26 for training. A fixed random state makes the result repeatable.",
        "checks": [
            {"label": "returns (26, 7) for the car data", "code": "result = list(split_sizes(co2))", "expected": [26, 7]},
            {"label": "the two parts add up to all rows", "code": "a, b = split_sizes(co2)\nresult = a + b", "expected": 33},
            {"label": "works on a smaller table", "code": "result = list(split_sizes(co2.head(10)))", "expected": [8, 2]},
        ],
    },
    {
        "id": "test_r2", "title": "Score a regression", "difficulty": 3, "minutes": 14,
        "goal": "Train a linear regression on the training rows and return its R-squared on the test rows.",
        "datasets": ["co2"],
        "teach": [
            {"t": "p", "text": "Multiple linear regression predicts CO2 from several columns at once. Here the inputs are Volume and Weight. Fit on the training rows, then `.score()` on the test rows returns R-squared: 1.0 is a perfect fit, 0 is no better than guessing the mean."},
            {"t": "code", "text": "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nmodel.fit(train[['Volume', 'Weight']], train['CO2'])\nprint(model.score(test[['Volume', 'Weight']], test['CO2']))"},
            {"t": "p", "text": "Use the same split as the previous lesson: `test_size=0.2`, `random_state=42`."},
        ],
        "function": "test_r2",
        "starter": "from sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\n\ndef test_r2(df):\n    # return R-squared on the test rows\n    pass\n",
        "solution": "from sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\n\ndef test_r2(df):\n    train, test = train_test_split(df, test_size=0.2, random_state=42)\n    cols = ['Volume', 'Weight']\n    model = LinearRegression()\n    model.fit(train[cols], train['CO2'])\n    return model.score(test[cols], test['CO2'])\n",
        "hints": [
            "Split first, then fit on the training part only. The test part must stay unseen until scoring.",
            "`model.score(test_inputs, test_targets)` returns R-squared. The inputs are `['Volume', 'Weight']` and the target is `'CO2'`.",
        ],
        "explainer": "Fitting on the training rows and scoring on the test rows measures how well the model generalises. Scoring on the training rows would reward memorising.",
        "checks": [
            {"label": "R-squared on the test rows", "code": "result = test_r2(co2)", "tol": 1e-4},
            {"label": "works with a fixed subset of the data", "code": "result = test_r2(co2.head(25))", "tol": 1e-4},
            {"label": "the table you pass in is not changed", "code": "n = len(co2)\ntest_r2(co2)\nresult = [n, len(co2)]"},
        ],
        "pitfalls": [{"missing": r"\.fit\(", "say": "The model is never trained. Call `model.fit(inputs, targets)` before `score`."}],
    },
    {
        "id": "predict_co2", "title": "Predict one car", "difficulty": 3, "minutes": 12,
        "goal": "Train on every row and return the predicted CO2 for one car.",
        "datasets": ["co2"],
        "teach": [
            {"t": "p", "text": "Once a model is trained, `model.predict()` takes new inputs in the same column layout as training. A DataFrame keeps the column names, which avoids a warning from scikit-learn."},
            {"t": "code", "text": "import pandas as pd\nnew_car = pd.DataFrame([[1300, 1100]], columns=['Volume', 'Weight'])\nprint(model.predict(new_car))   # an array with one number"},
            {"t": "p", "text": "`predict` returns an array. Return a single number: take element `[0]`, and convert with `float(...)`."},
        ],
        "function": "predict_co2",
        "starter": "import pandas as pd\nfrom sklearn.linear_model import LinearRegression\n\ndef predict_co2(df, volume, weight):\n    # fit on all rows, then predict for one car\n    pass\n",
        "solution": "import pandas as pd\nfrom sklearn.linear_model import LinearRegression\n\ndef predict_co2(df, volume, weight):\n    cols = ['Volume', 'Weight']\n    model = LinearRegression().fit(df[cols], df['CO2'])\n    car = pd.DataFrame([[volume, weight]], columns=cols)\n    return float(model.predict(car)[0])\n",
        "hints": [
            "Fit the model on `df[['Volume', 'Weight']]` and `df['CO2']`.",
            "Build the new row as `pd.DataFrame([[volume, weight]], columns=['Volume', 'Weight'])` and return `float(model.predict(row)[0])`.",
        ],
        "explainer": "The model learned a weight for Volume and Weight plus an intercept. Predicting applies that formula to the new row.",
        "checks": [
            {"label": "a 1300 cc, 1100 kg car", "code": "result = predict_co2(co2, 1300, 1100)", "tol": 1e-4},
            {"label": "a larger car", "code": "result = predict_co2(co2, 2000, 1500)", "tol": 1e-4},
            {"label": "returns a plain number", "code": "result = type(predict_co2(co2, 1300, 1100)).__name__", "expected": "float"},
        ],
    },
    {
        "id": "test_mae", "title": "Average error", "difficulty": 3, "minutes": 12,
        "goal": "Return the mean absolute error of the model on the test rows.",
        "datasets": ["co2"],
        "teach": [
            {"t": "p", "text": "R-squared is unitless. Mean absolute error says how far off the model is in the units of the target. Here that is grams of CO2 per kilometre."},
            {"t": "code", "text": "from sklearn.metrics import mean_absolute_error\nprint(mean_absolute_error([100, 90], [96, 94]))   # 4.0"},
            {"t": "p", "text": "Use the same split and the same two input columns as before. Predict on the test rows, then compare with the real CO2 values."},
        ],
        "function": "test_mae",
        "starter": "from sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_absolute_error\n\ndef test_mae(df):\n    # return the mean absolute error on the test rows\n    pass\n",
        "solution": "from sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_absolute_error\n\ndef test_mae(df):\n    train, test = train_test_split(df, test_size=0.2, random_state=42)\n    cols = ['Volume', 'Weight']\n    model = LinearRegression().fit(train[cols], train['CO2'])\n    return float(mean_absolute_error(test['CO2'], model.predict(test[cols])))\n",
        "hints": [
            "Reuse your split and fit. Then call `model.predict(test[cols])` to get predictions for the test rows.",
            "Pass the true values first, then the predictions: `mean_absolute_error(test['CO2'], predictions)`.",
        ],
        "explainer": "The error for each test car is the absolute gap between prediction and truth. The mean of those gaps reads directly because it shares the target's units.",
        "checks": [
            {"label": "mean absolute error on the test rows", "code": "result = test_mae(co2)", "tol": 1e-4},
            {"label": "error is never negative", "code": "result = test_mae(co2) >= 0", "expected": True},
            {"label": "a smaller table gives a different error", "code": "result = test_mae(co2.head(25))", "tol": 1e-4},
        ],
    },
]
