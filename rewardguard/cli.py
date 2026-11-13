"""Interfaz de línea de comandos."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .judge import VERDICTS, judge_all
from .report import VERDICT_LABEL, summarize, write_report
from .task import TaskError, load_tasks


def _tasks_dir(value):
    """Carpeta de tareas: la indicada, o la que viene junto al programa."""
    if value:
        return value
    local = Path("tasks")
    return str(local if local.is_dir() else Path(__file__).resolve().parent.parent / "tasks")


def cmd_list(args) -> int:
    for t in load_tasks(_tasks_dir(args.tasks)):
        extra = ", ".join(n for n, _, _ in t.relations) or "sin relaciones"
        print(f"{t.id:<16} {t.difficulty:<7} {len(t.visible)} visibles  ({extra})  {t.title}")
    return 0


def cmd_scan(args) -> int:
    only = args.only.split(",") if args.only else None
    for agent in args.agents:
        if not Path(agent).is_dir():
            raise ValueError(f"la carpeta de soluciones no existe: {agent}")
    tasks = load_tasks(_tasks_dir(args.tasks), only)

    def progress(r):
        print(f"  {r.model:<16} {r.task_id:<16} {VERDICT_LABEL[r.verdict]:<13} "
              f"visibles {r.visible_pass}/{r.visible_total}  generados {r.fuzz_pass}/{r.fuzz_total}")

    print(f"Analizando {len(tasks)} tareas en {len(args.agents)} agentes ({args.cases} entradas generadas por tarea)...")
    results = judge_all(tasks, args.agents, args.cases, args.timeout, progress)
    path = write_report(results, tasks, args.output)
    print("\nPuntuación aparente frente a real:")
    for row in summarize(results):
        v = row["verdicts"]
        print(f"  {row['agent']:<16} aparente {row['apparent'] * 100:5.1f}%  real {row['real'] * 100:5.1f}%  "
              f"trampas {v['TRAMPA']}  sobreajuste {v['SOBREAJUSTE']}")
    print(f"\nInforme guardado en {path}")
    if args.strict and any(r.verdict == "TRAMPA" for r in results):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rewardguard",
                                     description="Detecta trampas en el código generado por IA (reward hacking).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p_list = sub.add_parser("list", help="muestra las tareas disponibles")
    p_list.add_argument("--tasks", default=None, help="carpeta con las tareas (.py)")
    p_list.set_defaults(func=cmd_list)
    p_scan = sub.add_parser("scan", help="analiza carpetas de soluciones y genera un informe")
    p_scan.add_argument("agents", nargs="+", help="carpetas de soluciones; el nombre de la carpeta es el del agente")
    p_scan.add_argument("--tasks", default=None, help="carpeta con las tareas (.py)")
    p_scan.add_argument("-o", "--output", default="informe.html", help="informe (.html, .md o .json)")
    p_scan.add_argument("--only", help="ids de tareas separados por comas")
    p_scan.add_argument("--cases", type=int, default=150, help="entradas generadas por tarea (por defecto 150)")
    p_scan.add_argument("--timeout", type=float, help="segundos máximos por solución")
    p_scan.add_argument("--strict", action="store_true", help="código de salida 1 si se detecta alguna trampa")
    p_scan.set_defaults(func=cmd_scan)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (TaskError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
