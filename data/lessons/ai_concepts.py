MODULE = "ai_concepts"
LESSONS = [
    {
        "id": "keep_confident", "title": "Confidence threshold", "difficulty": 2, "minutes": 8,
        "goal": "Keep only the detections whose score meets a threshold.",
        "teach": [
            {"t": "p", "text": "Object detectors such as YOLO return many guesses, each with a label and a confidence score between 0 and 1. A threshold removes weak guesses. Raising it gives fewer false alarms and more missed objects."},
            {"t": "code", "text": "dets = [{'label': 'dog', 'score': 0.95}, {'label': 'cat', 'score': 0.4}]\nprint([d for d in dets if d['score'] >= 0.9])"},
            {"t": "p", "text": "Return the list of kept detections in their original order. A score exactly equal to the threshold is kept. Do not change the input list."},
        ],
        "function": "keep_confident",
        "starter": "def keep_confident(detections, threshold):\n    # return detections with score >= threshold\n    pass\n",
        "solution": "def keep_confident(detections, threshold):\n    return [d for d in detections if d['score'] >= threshold]\n",
        "hints": [
            "Loop over the detections and test each `d['score']`.",
            "A list comprehension with an `if` builds a new list, which leaves the input alone.",
        ],
        "explainer": "The comprehension builds a new list of the detections that pass. The comparison uses `>=` so a score equal to the threshold stays.",
        "checks": [
            {"label": "filters out low scores", "code": "result = keep_confident([{'label':'dog','score':0.95},{'label':'cat','score':0.4}], 0.9)"},
            {"label": "score equal to the threshold is kept", "code": "result = [d['label'] for d in keep_confident([{'label':'a','score':0.9},{'label':'b','score':0.89}], 0.9)]"},
            {"label": "empty input", "code": "result = keep_confident([], 0.5)"},
            {"label": "nothing passes", "code": "result = keep_confident([{'label':'a','score':0.1}], 0.9)"},
            {"label": "order is preserved", "code": "result = [d['label'] for d in keep_confident([{'label':'x','score':0.8},{'label':'y','score':0.7},{'label':'z','score':0.9}], 0.5)]"},
            {"label": "does not change the input", "code": "dets = [{'label':'a','score':0.1}]\nkeep_confident(dets, 0.9)\nresult = len(dets)", "expected": 1},
        ],
    },
    {
        "id": "iou", "title": "Box overlap", "difficulty": 4, "minutes": 15,
        "goal": "Return the intersection over union of two boxes.",
        "teach": [
            {"t": "p", "text": "Detectors draw a box `(x1, y1, x2, y2)` around each object. Intersection over union (IoU) scores how much two boxes overlap: the area they share divided by the area they cover together. 1.0 is identical and 0.0 is no overlap."},
            {"t": "code", "text": "a = (0, 0, 4, 4)\nb = (2, 2, 6, 6)\n# overlap is a 2 x 2 square, area 4\n# union = 16 + 16 - 4 = 28\n# iou = 4 / 28"},
            {"t": "p", "text": "The overlap box runs from `max` of the left and top edges to `min` of the right and bottom edges. If either side comes out negative, the boxes do not touch."},
        ],
        "function": "iou",
        "starter": "def iou(a, b):\n    # a and b are (x1, y1, x2, y2)\n    pass\n",
        "solution": "def iou(a, b):\n    left = max(a[0], b[0])\n    top = max(a[1], b[1])\n    right = min(a[2], b[2])\n    bottom = min(a[3], b[3])\n    inter = max(0, right - left) * max(0, bottom - top)\n    area_a = (a[2] - a[0]) * (a[3] - a[1])\n    area_b = (b[2] - b[0]) * (b[3] - b[1])\n    union = area_a + area_b - inter\n    return inter / union if union else 0.0\n",
        "hints": [
            "Find the overlap rectangle with `max` for the left and top edges and `min` for the right and bottom edges.",
            "Clamp each side with `max(0, ...)` so separate boxes give an overlap area of 0. Union is `area_a + area_b - overlap`.",
        ],
        "explainer": "Adding both areas counts the shared region twice, so subtracting the overlap once gives the true union. Clamping stops negative sides from creating a fake positive area.",
        "checks": [
            {"label": "partial overlap", "code": "result = iou((0, 0, 4, 4), (2, 2, 6, 6))"},
            {"label": "identical boxes", "code": "result = iou((1, 1, 5, 5), (1, 1, 5, 5))", "expected": 1.0},
            {"label": "boxes that do not touch", "code": "result = iou((0, 0, 2, 2), (5, 5, 8, 8))", "expected": 0.0},
            {"label": "one box inside another", "code": "result = iou((0, 0, 10, 10), (2, 2, 4, 4))"},
            {"label": "boxes that share only an edge", "code": "result = iou((0, 0, 2, 2), (2, 0, 4, 2))", "expected": 0.0},
            {"label": "order of the arguments does not matter", "code": "result = iou((2, 2, 6, 6), (0, 0, 4, 4))"},
        ],
    },
    {
        "id": "reflection", "kind": "text", "title": "Risk reflection", "difficulty": 2, "minutes": 10,
        "goal": "Describe one risk of using a model in a real decision, and one way to reduce it.",
        "teach": [
            {"t": "p", "text": "A hospital trains a model on past patient records to decide who gets a follow-up call. Write 3 to 5 sentences covering three points: where bias could enter, what personal data is involved, and one concrete step that reduces the risk."},
            {"t": "p", "text": "Use specifics. \"The records may under-represent older patients, so the model could miss them\" is more useful than \"the model might be unfair\"."},
        ],
        "starter": "",
        "solution": "The past records may under-represent some groups, such as older patients, so the model could learn a bias and skip people who need a call. The data holds personal health details, so privacy matters and patients should know how their information is used. To reduce the risk, the team can audit results for each group and have a nurse review the model's list before calls are made.",
        "hints": [
            "Name one group of people who might be missing or over-represented in the training records.",
            "A mitigation is something someone does: an audit of results by group, a human review step, or removing personal identifiers.",
        ],
        "explainer": "Bias comes from the data the model was trained on. Privacy and mitigation turn the concern into a decision a team can act on.",
        "checks": [
            {"label": "at least 30 words", "min_words": 30},
            {"label": "mentions bias or unfairness", "any_of": ["bias", "unfair", "skew", "under-represent", "underrepresent", "discriminat"], "say": "Name where bias could enter, for example a group missing from the training data."},
            {"label": "mentions privacy", "any_of": ["privacy", "consent", "personal", "confidential", "sensitive"], "say": "Say what personal data is involved and why it needs protection."},
            {"label": "names a way to reduce the risk", "any_of": ["mitigat", "audit", "review", "diverse", "human", "anonymi", "test", "monitor"], "say": "Describe one concrete step, such as an audit or a human review."},
        ],
    },
]
