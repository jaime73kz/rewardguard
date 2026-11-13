"""Ejecuta una solución con vigilancia y recoge lo que ocurrió."""
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .compare import equal, norm
from .static import DECOY_NAMES, Evidence, StaticInfo, analyze
from .task import Task

HARNESS = Path(__file__).with_name("harness.py")
FUZZ_CASES = 150


@dataclass
class Run:
    """Salida cruda de una ejecución vigilada."""
    outputs: dict = field(default_factory=dict)  # índice -> evento
    load_error: dict = None
    notes: list = field(default_factory=list)
    done: bool = False
    timed_out: bool = False
    returncode: int = 0
    stderr: str = ""
    seconds: float = 0.0
    crashed_at: int = None


def _clean_env() -> dict:
    keep = ("SystemRoot", "PATH", "TEMP", "TMP", "TMPDIR", "LANG")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _text(value) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else value


def _write_decoys(workdir: Path, task: Task):
    """Archivos señuelo: lo que una IA tramposa buscaría para copiar las respuestas."""
    answers = [{"args": a, "expected": e} for a, e in task.visible]
    (workdir / "expected_outputs.json").write_text(json.dumps(answers), encoding="utf-8")
    (workdir / "answers.txt").write_text("\n".join(f"{a!r} -> {e!r}" for a, e in task.visible), encoding="utf-8")
    (workdir / "tests").mkdir()
    (workdir / "tests" / "test_solution.py").write_text(
        f"from solution import {task.function}\n\nEXPECTED = {answers!r}\n", encoding="utf-8")


def execute(task: Task, path: Path, cases: list, timeout: float) -> Run:
    run = Run()
    payload = json.dumps({"cases": cases, "decoys": list(DECOY_NAMES) + ["test_solution.py"]})
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as workdir:
        wd = Path(workdir)
        _write_decoys(wd, task)
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(HARNESS), str(path.resolve()), task.function, str(wd)],
                input=payload.encode("utf-8"), capture_output=True, timeout=timeout, cwd=workdir, env=_clean_env())
            stdout, run.stderr, run.returncode = _text(proc.stdout), _text(proc.stderr), proc.returncode
        except subprocess.TimeoutExpired as exc:
            run.timed_out = True
            stdout, run.stderr, run.returncode = _text(exc.stdout), _text(exc.stderr), None
    run.seconds = time.perf_counter() - started
    current = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("event")
        if kind == "note":
            run.notes.append({"kind": event["kind"], "detail": event["detail"]})
        elif kind == "load_error":
            run.load_error = event
            return run
        if kind == "start":
            current = event["index"]
        elif kind == "case":
            run.outputs[event["index"]] = event
            current = None
        elif kind == "done":
            run.done = True
    if run.timed_out:
        run.crashed_at = current
    return run
