// ES module worker (importScripts is blocked in some embedded browsers).
// Runs submitted Python off the main thread. The page kills and respawns this
// worker when a run takes too long, so an endless loop cannot freeze the tab.
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.3/full/pyodide.mjs";
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.3/full/";

let pyodide = null;
let ready = null;
const loaded = new Set();

function say(msg) { postMessage({ type: "status", msg }); }

async function init(runnerSource) {
  say("Starting Python");
  pyodide = await loadPyodide({ indexURL: PYODIDE });
  pyodide.FS.writeFile("/home/pyodide/runner.py", runnerSource);
  postMessage({ type: "ready" });
}

async function ensurePackages(source) {
  const names = new Set();
  for (const m of source.matchAll(/^\s*(?:from|import)\s+([a-zA-Z0-9_]+)/gm)) names.add(m[1]);
  const map = { sklearn: "scikit-learn", numpy: "numpy", pandas: "pandas", scipy: "scipy" };
  const want = [...names].map((n) => map[n]).filter((p) => p && !loaded.has(p));
  if (!want.length) return;
  say("Loading " + want.join(", ") + " (first time only)");
  await pyodide.loadPackage(want);
  want.forEach((p) => loaded.add(p));
}

onmessage = async (e) => {
  const msg = e.data;
  try {
    if (msg.type === "init") {
      ready = init(msg.runner);
      await ready;
      return;
    }
    await ready;
    if (msg.type === "run" || msg.type === "check") {
      const l = msg.lesson;
      let src = msg.code + "\n" + (l.setup || "");
      if (l.datasets && l.datasets.length) src += "\nimport pandas\n";
      (l.checks || []).forEach((c) => { if (c.code) src += "\n" + c.code; });
      await ensurePackages(src);
      postMessage({ type: "running", id: msg.id });
      pyodide.globals.set("_lesson_json", JSON.stringify(l));
      pyodide.globals.set("_datasets_json", JSON.stringify(msg.datasets));
      pyodide.globals.set("_code", msg.code);
      const fn = msg.type === "run" ? "run_only" : "run_lesson";
      const out = await pyodide.runPythonAsync(
        "import json, runner\n" +
        "json.dumps(runner." + fn + "(json.loads(_lesson_json), _code, json.loads(_datasets_json)))"
      );
      postMessage({ type: "result", id: msg.id, result: JSON.parse(out) });
    }
  } catch (err) {
    postMessage({ type: "fatal", id: msg.id, message: String(err && err.message || err) });
  }
};
