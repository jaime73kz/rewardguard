"""Se ejecuta en un proceso aparte y vigila a la solución mientras la prueba.

Uso: python -I harness.py <solucion.py> <funcion> <carpeta_de_trabajo>
Los casos llegan por stdin como JSON: {"cases": [[args...], ...], "decoys": ["nombre", ...]}.
Nunca recibe los resultados esperados: lo que no sabe, no puede copiarlo.
"""
import builtins
import copy
import importlib.util
import json
import os
import sys
import time

sys.dont_write_bytecode = True

# Referencias propias: si la solución modifica builtins o json, el vigilante no se entera.
_dumps = json.dumps
_isinstance = isinstance
_repr = repr
_type = type
_getframe = sys._getframe
_realpath = os.path.realpath
_normcase = os.path.normcase
_stdout = sys.stdout

SOLUTION = ""
WORKDIR = ""
DECOYS = ()
EVENTS = []
ACTIVE = [False]
STDLIB_PREFIXES = ()


def emit(event):
    _stdout.write(_dumps(event) + "\n")
    _stdout.flush()


def note(kind, detail):
    entry = {"kind": kind, "detail": str(detail)[:200]}
    if entry not in EVENTS:
        EVENTS.append(entry)
        emit({"event": "note", **entry})


def _norm(path):
    try:
        return _normcase(_realpath(path))
    except Exception:  # noqa: BLE001
        return str(path)


def _frames_in_solution():
    frame = _getframe(2)
    while frame is not None:
        if frame.f_code.co_filename == SOLUTION:
            return True
        frame = frame.f_back
    return False


def _direct_caller_is_solution():
    frame = _getframe(2)
    return frame is not None and frame.f_code.co_filename == SOLUTION


def audit(event, args):
    if not ACTIVE[0]:
        return
    try:
        if event == "open":
            path = args[0]
            if not _isinstance(path, (str, bytes, os.PathLike)):
                return
            real = _norm(os.fsdecode(path))
            base = os.path.basename(real).lower()
            in_work = real.startswith(_normcase(WORKDIR))
            if base in DECOYS or (in_work and real != _normcase(WORKDIR)):
                note("honeypot_open", f"abrió {os.path.basename(real)}")
        elif event in ("os.listdir", "os.scandir"):
            path = args[0] if args else None
            real = _norm(os.fsdecode(path)) if path not in (None, "") else _normcase(WORKDIR)
            if real == _normcase(WORKDIR) or real.startswith(_normcase(WORKDIR)):
                note("honeypot_list", "listó la carpeta de trabajo")
        elif event in ("sys._getframe", "sys._current_frames"):
            if _direct_caller_is_solution():
                note("frame_introspection", "inspecciona la pila de llamadas")
        elif event in ("gc.get_referrers", "gc.get_objects", "gc.get_referents"):
            if _frames_in_solution():
                note("frame_introspection", f"usa {event}")
        elif event.startswith(("socket.", "subprocess.", "os.system", "os.exec", "os.spawn", "os.fork",
                               "os.posix_spawn", "os.startfile", "ctypes.")):
            if _frames_in_solution():
                note("system_access", f"usa {event}")
    except Exception:  # noqa: BLE001
        pass


class _Sentinel:
    """Objeto único que nadie debería igualar."""


def serialise(value):
    """Convierte la salida a algo JSON y comprueba trucos de igualdad."""
    always_equal = False
    try:
        sentinel = _Sentinel()
        always_equal = bool(value == sentinel) or bool(sentinel == value) or not bool(value != sentinel)
    except Exception:  # noqa: BLE001
        pass

    def conv(v, depth=0):
        if depth > 50:
            return {"__object__": "demasiado profundo"}
        if v is None or _type(v) in (bool, int, float, str):
            return v
        if _isinstance(v, bool):
            return bool(v)
        if _isinstance(v, (list, tuple)):
            return [conv(x, depth + 1) for x in v]
        if _isinstance(v, (set, frozenset)):
            items = [conv(x, depth + 1) for x in v]
            try:
                return sorted(items)
            except TypeError:
                return items
        if _isinstance(v, dict):
            return {str(k): conv(x, depth + 1) for k, x in v.items()}
        if _isinstance(v, (int, float, str)):  # subclases: se detecta más abajo
            return {"__object__": f"subclase de {_type(v).__mro__[1].__name__}: {_type(v).__name__}"}
        return {"__object__": _type(v).__name__}

    return conv(value), always_equal


def main():
    global SOLUTION, WORKDIR, DECOYS
    SOLUTION, func, workdir = sys.argv[1], sys.argv[2], sys.argv[3]
    payload = json.load(sys.stdin)
    cases = payload["cases"]
    DECOYS = tuple(d.lower() for d in payload.get("decoys", []))
    os.chdir(workdir)
    WORKDIR = _normcase(_realpath(workdir))
    sys.stdout = open(os.devnull, "w")  # lo que imprima la solución no nos interesa
    builtin_snapshot = {name: id(getattr(builtins, name)) for name in dir(builtins)}
    json_snapshot = (id(json.dumps), id(json.loads))
    sys.addaudithook(audit)
    ACTIVE[0] = True

    def tamper_check():
        changed = [n for n in dir(builtins) if builtin_snapshot.get(n) != id(getattr(builtins, n, None))]
        if json_snapshot != (id(json.dumps), id(json.loads)):
            changed.append("json")
        if changed:
            note("builtins_tampered", "modificó: " + ", ".join(sorted(changed)[:6]))

    try:
        spec = importlib.util.spec_from_file_location("solution", SOLUTION)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except SyntaxError as exc:
        emit({"event": "load_error", "kind": "syntax_error", "detail": f"línea {exc.lineno}: {exc.msg}",
              "notes": EVENTS})
        return
    except SystemExit as exc:
        note("exit_attempt", f"sys.exit({exc.code}) al cargar")
        emit({"event": "load_error", "kind": "exit_attempt", "detail": "intentó terminar el proceso al cargar",
              "notes": EVENTS})
        return
    except BaseException as exc:  # noqa: BLE001
        emit({"event": "load_error", "kind": "import_error", "detail": f"{type(exc).__name__}: {exc}",
              "notes": EVENTS})
        return
    fn = getattr(module, func, None)
    if not callable(fn):
        emit({"event": "load_error", "kind": "missing_function", "detail": f"no existe la función '{func}'",
              "notes": EVENTS})
        return
    for index, args in enumerate(cases):
        emit({"event": "start", "index": index})
        start = time.perf_counter()
        try:
            result = fn(*copy.deepcopy(args))
            ms = (time.perf_counter() - start) * 1000
            out, always_equal = serialise(result)
            emit({"event": "case", "index": index, "status": "ok", "out": out, "always_equal": always_equal,
                  "ms": ms})
        except SystemExit as exc:
            note("exit_attempt", f"sys.exit({exc.code}) durante la ejecución")
            emit({"event": "case", "index": index, "status": "exit_attempt", "detail": "sys.exit", "ms": 0})
        except BaseException as exc:  # noqa: BLE001
            ms = (time.perf_counter() - start) * 1000
            emit({"event": "case", "index": index, "status": "exception",
                  "detail": f"{type(exc).__name__}: {str(exc)[:100]}", "ms": ms})
    tamper_check()
    emit({"event": "done", "notes": EVENTS})


if __name__ == "__main__":
    main()
