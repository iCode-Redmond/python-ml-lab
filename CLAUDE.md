# ML Lab: working notes

Static, in-browser Python lab covering machine learning basics. No framework, no bundler, no LLM calls.
Python runs in Pyodide inside a module Web Worker (`worker.js`).

## Layout
- `data/lessons/<module>.py` lessons as Python dicts (`LESSONS`). Order comes from `data/course.json`.
- `data/datasets/*.csv` injected into lessons as DataFrames named by file stem.
- `engine/runner.py` grades code. Runs in CPython (validate) and Pyodide (browser). Do not add imports that Pyodide lacks.
- `tools/validate.py` the gate. `tools/build.py` writes `app-data.js` and refuses on any failure. `app-data.js` is generated.
- `tools/test_validate.py` fixtures that try to fool the gate. Run it after touching `validate.py`.
- `tools/test_runner.py` unit tests for the runner (Run output, error lines, diagnoses). Run it after touching `engine/runner.py`.
- `docs/voice.md` the writing rules. Read before writing lesson text.

```bash
.venv/bin/python tools/validate.py && .venv/bin/python tools/test_validate.py && .venv/bin/python tools/test_runner.py
.venv/bin/python tools/build.py
python3 -m http.server 8765      # then open /index.html
```
Setup: `uv venv --python 3.14 .venv && uv pip install --python .venv/bin/python pandas scikit-learn scipy numpy`

## Rules
- `expected` values come from running `solution`. Pin one by hand only when an external reference states it, and the gate checks the solution agrees.
- A check's `code` sets `result`. Keep results JSON-native (`list(...)`, `float(...)`).
- Float checks from sklearn use `"tol": 1e-4`. CPython and Pyodide builds can differ in the last digits.
- `pitfalls` are regex hints on failure. They must not match the solution (gate enforces it).
- Run calls the lesson function on a sample input. It uses `try` if set, else the first check's one-line call. Set `try` when the first check is multi-line.
- Starter code must fail every check. A constant-returning function must fail too.
- Fix random seeds in the lesson text (`random_state=42`).
- Verify in Pyodide before calling a change done. CPython passing does not prove it.

## Browser notes
- Use `type: "module"` for the worker. `importScripts` of the Pyodide CDN failed in the embedded browser pane.
- Runs stop after 20 s. The worker is killed and respawned.
- Progress lives in localStorage under `storageKey`. Export and Import move it between machines.

## Reusing for another course
Copy the folder. Replace `data/course.json`, `data/lessons/*.py`, `data/datasets/*`. Keep `engine/`, `tools/`, `worker.js`, `index.html`.

## Not done
- Jev (TypeSafe) layer for the free-text reflection. Deterministic keyword checks cover it today.
- Lessons on multimodal AI and computer vision beyond the two detection exercises.
- Sentiment uses a small bundled lexicon, not NLTK VADER, so scores differ from VADER output.
