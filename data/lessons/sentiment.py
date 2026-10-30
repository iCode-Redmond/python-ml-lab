MODULE = "sentiment"

SETUP = '''LEXICON = {
    "love": 0.9, "great": 0.8, "happy": 0.7, "fun": 0.6, "good": 0.5, "nice": 0.4,
    "boring": -0.6, "bad": -0.5, "sad": -0.7, "awful": -0.8, "terrible": -0.9, "hate": -0.9,
}
'''

LESSONS = [
    {
        "id": "word_score", "title": "Score one word", "difficulty": 1, "minutes": 6,
        "goal": "Return the sentiment score of one word from the dictionary LEXICON, or 0 if the word is not listed.",
        "setup": SETUP,
        "teach": [
            {"t": "p", "text": "Sentiment analysis rates how positive or negative text is. The simplest version looks each word up in a lexicon, a dictionary that maps words to scores between -1 and 1. The lexicon is already defined for you as `LEXICON`."},
            {"t": "code", "text": "print(LEXICON[\"great\"])            # 0.8\nprint(LEXICON.get(\"table\", 0))     # 0  (not in the lexicon)"},
            {"t": "p", "text": "Use `.get(key, default)` so an unknown word does not raise a KeyError. Lowercase the word first, because the lexicon keys are lowercase."},
        ],
        "function": "word_score",
        "starter": "def word_score(word):\n    # look up word in LEXICON, ignoring capital letters\n    pass\n",
        "solution": "def word_score(word):\n    return LEXICON.get(word.lower(), 0)\n",
        "hints": [
            "Dictionaries have a `.get()` method that takes a fallback value.",
            "Call `word.lower()` before the lookup so \"Great\" matches \"great\".",
        ],
        "explainer": "`.get` returns the fallback instead of failing when the key is missing. Lowercasing makes the lookup ignore capital letters.",
        "checks": [
            {"label": "a positive word", "code": "result = word_score('great')"},
            {"label": "a negative word", "code": "result = word_score('terrible')"},
            {"label": "capital letters are ignored", "code": "result = word_score('Love')"},
            {"label": "an unknown word scores 0", "code": "result = word_score('table')"},
            {"label": "the empty string scores 0", "code": "result = word_score('')"},
        ],
    },
    {
        "id": "text_score", "title": "Score a sentence", "difficulty": 2, "minutes": 10,
        "goal": "Return the mean word score of a sentence. Return 0.0 for an empty sentence.",
        "setup": SETUP,
        "teach": [
            {"t": "p", "text": "A sentence score is the mean of its word scores. Split the text into words, strip punctuation from each, score each, then average."},
            {"t": "code", "text": "text = \"Great, fun!\"\nwords = [w.strip(\".,!?\") for w in text.split()]\nprint(words)   # ['Great', 'fun']"},
            {"t": "p", "text": "`LEXICON` is available. You can write your own helper, or look words up directly. Unknown words count as 0 and still count toward the length, so neutral words pull the mean toward zero."},
        ],
        "function": "text_score",
        "starter": "def text_score(text):\n    # mean score of the words in text\n    pass\n",
        "solution": "def text_score(text):\n    words = [w.strip('.,!?;:\"').lower() for w in text.split()]\n    if not words:\n        return 0.0\n    return sum(LEXICON.get(w, 0) for w in words) / len(words)\n",
        "hints": [
            "Split on spaces, then strip punctuation from each word before the lookup.",
            "Guard against an empty list first, because dividing by `len(words)` would fail when it is 0.",
        ],
        "explainer": "Cleaning each word lets \"great,\" match \"great\". The empty check avoids a division by zero, and counting unknown words keeps long neutral sentences from looking extreme.",
        "checks": [
            {"label": "one positive word with punctuation", "code": "result = text_score('Great!')"},
            {"label": "mixed sentence", "code": "result = text_score('I love good food but hate rain')"},
            {"label": "all unknown words", "code": "result = text_score('the table is wooden')"},
            {"label": "empty text", "code": "result = text_score('')"},
            {"label": "capital letters", "code": "result = text_score('GOOD Bad')"},
        ],
        "pitfalls": [{"missing": r"len\(", "say": "A mean needs the number of words. Use `len(words)`."}],
    },
    {
        "id": "reaction", "title": "Label the score", "difficulty": 1, "minutes": 6,
        "goal": "Turn a score into one of five labels.",
        "teach": [
            {"t": "p", "text": "Models output numbers, and people read labels. A chain of `if` and `elif` picks the first rule that is true, so the order of the rules matters."},
            {"t": "code", "text": "score = 0.7\nif score > 0.5:\n    print('very positive')\nelif score > 0:\n    print('positive')"},
            {"t": "p", "text": "Rules for `reaction(score)`: above 0.5 is \"very positive\", above 0 is \"positive\", exactly 0 is \"neutral\", below -0.5 is \"very negative\", anything else is \"negative\"."},
        ],
        "function": "reaction",
        "starter": "def reaction(score):\n    # return one of five labels\n    pass\n",
        "solution": "def reaction(score):\n    if score > 0.5:\n        return 'very positive'\n    if score > 0:\n        return 'positive'\n    if score == 0:\n        return 'neutral'\n    if score < -0.5:\n        return 'very negative'\n    return 'negative'\n",
        "hints": [
            "Check the strongest case first. A score of 0.9 is above 0, but it should be \"very positive\".",
            "Handle the positive side top-down, then 0, then the negative side with `< -0.5` before the final fallback.",
        ],
        "explainer": "Each `if` returns immediately, so later rules only run for scores the earlier ones rejected. Testing the boundaries 0.5, 0 and -0.5 is what the checks do.",
        "checks": [
            {"label": "0.9", "code": "result = reaction(0.9)", "expected": "very positive"},
            {"label": "exactly 0.5 is not very positive", "code": "result = reaction(0.5)", "expected": "positive"},
            {"label": "0.1", "code": "result = reaction(0.1)", "expected": "positive"},
            {"label": "exactly 0", "code": "result = reaction(0)", "expected": "neutral"},
            {"label": "-0.2", "code": "result = reaction(-0.2)", "expected": "negative"},
            {"label": "exactly -0.5 is not very negative", "code": "result = reaction(-0.5)", "expected": "negative"},
            {"label": "-0.9", "code": "result = reaction(-0.9)", "expected": "very negative"},
        ],
    },
]
