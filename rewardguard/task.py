"""Tareas: módulos de Python con enunciado, tests visibles, referencia y generador."""
import importlib.util
import random
from dataclasses import dataclass, field
from pathlib import Path


class TaskError(ValueError):
    """La tarea es inválida."""


@dataclass
class Task:
    id: str
    title: str
    difficulty: str
    function: str
    prompt: str
    visible: list  # [(args, expected)]
    reference: object
    generate: object
    check: object = None  # (args, salida) -> bool; sustituye a la igualdad con la referencia
    relations: list = field(default_factory=list)  # [(nombre, transforma(args, rng), compara(salida1, salida2))]
    timeout: float = 10.0

    def expected_for(self, args):
        return self.reference(*args)

    def fuzz_cases(self, n: int, seed: int = 12345) -> list:
        rng = random.Random(f"{seed}:{self.id}")
        return [self.generate(rng) for _ in range(n)]

    def relation_cases(self, base_cases: list, seed: int = 777) -> list:
        """Devuelve [(indice_relacion, args_originales, args_transformados)]."""
        rng = random.Random(f"{seed}:{self.id}")
        out = []
        for r_index, (_, transform, _) in enumerate(self.relations):
            for args in base_cases[:12]:
                out.append((r_index, args, transform(list(args), rng)))
        return out


def load_task(path) -> Task:
    path = Path(path)
    spec = importlib.util.spec_from_file_location(f"rg_task_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        raise TaskError(f"{path.name}: no se pudo cargar ({type(exc).__name__}: {exc})") from exc
    for name in ("ID", "FUNCTION", "PROMPT", "VISIBLE", "reference", "generate"):
        if not hasattr(module, name):
            raise TaskError(f"{path.name}: falta '{name}'")
    if not module.VISIBLE:
        raise TaskError(f"{path.name}: VISIBLE no puede estar vacío")
    return Task(
        id=module.ID, title=getattr(module, "TITLE", module.ID), difficulty=getattr(module, "DIFFICULTY", "medium"),
        function=module.FUNCTION, prompt=module.PROMPT.strip(), visible=list(module.VISIBLE),
        reference=module.reference, generate=module.generate, check=getattr(module, "CHECK", None),
        relations=list(getattr(module, "RELATIONS", [])), timeout=float(getattr(module, "TIMEOUT", 10.0)),
    )


def load_tasks(directory, only=None) -> list:
    directory = Path(directory)
    if not directory.is_dir():
        raise TaskError(f"No existe la carpeta de tareas: {directory}")
    tasks = [load_task(p) for p in sorted(directory.glob("*.py")) if not p.name.startswith("_")]
    if only:
        tasks = [t for t in tasks if t.id in set(only)]
    if not tasks:
        raise TaskError("No se encontró ninguna tarea.")
    return tasks
