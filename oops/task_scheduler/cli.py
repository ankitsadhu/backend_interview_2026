"""
cli.py — Rich-powered CLI for the Task Scheduler.

Commands:
    add      Add a new task
    list     List all registered tasks
    remove   Remove a task by ID
    pause    Pause a task
    resume   Resume a paused task
    history  Show execution history for a task
    run      One-shot execute a task immediately
    start    Start the live scheduler (Ctrl+C to stop)
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box

# We import locally constructed tasks for demo functions
from scheduler import TaskScheduler, Task, Priority, CronExpression

console = Console()
DB_PATH = "tasks.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _priority_colour(p: Priority) -> str:
    return {
        Priority.CRITICAL: "bold red",
        Priority.HIGH    : "orange3",
        Priority.NORMAL  : "green",
        Priority.LOW     : "dim",
    }.get(p, "white")


def _status_colour(s: str) -> str:
    return {
        "PENDING"  : "cyan",
        "RUNNING"  : "bold yellow",
        "SUCCESS"  : "bold green",
        "FAILED"   : "bold red",
        "PAUSED"   : "dim magenta",
        "CANCELLED": "dim red",
    }.get(s, "white")


def _tasks_table(scheduler: TaskScheduler) -> Table:
    table = Table(
        title="[bold cyan]Registered Tasks[/]",
        box=box.ROUNDED,
        show_lines=True,
        highlight=True,
    )
    table.add_column("ID (short)",   style="dim",    no_wrap=True)
    table.add_column("Name",         style="bold")
    table.add_column("Cron",         style="cyan",   no_wrap=True)
    table.add_column("Priority",     no_wrap=True)
    table.add_column("Status",       no_wrap=True)
    table.add_column("Retries",      justify="right")
    table.add_column("Next Run (UTC)")
    table.add_column("Last Run (UTC)")
    table.add_column("Tags")

    for task in scheduler.list_tasks():
        pcolor = _priority_colour(task.priority)
        scolor = _status_colour(task.status.value)
        table.add_row(
            task.id[:8],
            task.name,
            str(task.cron),
            f"[{pcolor}]{task.priority.name}[/]",
            f"[{scolor}]{task.status.value}[/]",
            str(task.retry_count),
            task.next_run.strftime("%Y-%m-%d %H:%M:%S") if task.next_run else "-",
            task.last_run.strftime("%Y-%m-%d %H:%M:%S") if task.last_run else "-",
            ", ".join(task.tags) or "-",
        )
    return table


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> None:
    scheduler = TaskScheduler(persist_path=DB_PATH)

    # For CLI-added tasks the callable is a no-op placeholder
    def _placeholder(*a, **kw):
        print(f"[task '{args.name}' executed at {datetime.utcnow().isoformat()}]")

    priority = Priority[args.priority.upper()]
    task = Task(
        name        = args.name,
        cron        = CronExpression(args.cron),
        func        = _placeholder,
        priority    = priority,
        retry_count = args.retries,
        timeout     = args.timeout,
        tags        = args.tags.split(",") if args.tags else [],
    )
    task_id = scheduler.add_task(task)
    console.print(f"[bold green]✓ Task added:[/] [cyan]{task.name}[/] (id: [dim]{task_id}[/])")


def cmd_list(args: argparse.Namespace) -> None:
    scheduler = TaskScheduler(persist_path=DB_PATH)
    tasks = scheduler.list_tasks()
    if not tasks:
        console.print("[dim]No tasks registered.[/]")
        return
    console.print(_tasks_table(scheduler))


def cmd_remove(args: argparse.Namespace) -> None:
    scheduler = TaskScheduler(persist_path=DB_PATH)
    # Support short ID lookup
    full_id = _resolve_id(scheduler, args.id)
    if scheduler.remove_task(full_id):
        console.print(f"[bold red]✗ Removed task[/] [dim]{full_id}[/]")
    else:
        console.print(f"[red]Task not found:[/] {args.id}")


def cmd_pause(args: argparse.Namespace) -> None:
    scheduler = TaskScheduler(persist_path=DB_PATH)
    full_id = _resolve_id(scheduler, args.id)
    if scheduler.pause_task(full_id):
        console.print(f"[magenta]⏸  Paused task[/] [dim]{full_id}[/]")
    else:
        console.print(f"[red]Task not found:[/] {args.id}")


def cmd_resume(args: argparse.Namespace) -> None:
    scheduler = TaskScheduler(persist_path=DB_PATH)
    full_id = _resolve_id(scheduler, args.id)
    if scheduler.resume_task(full_id):
        console.print(f"[green]▶  Resumed task[/] [dim]{full_id}[/]")
    else:
        console.print(f"[red]Task not found:[/] {args.id}")


def cmd_history(args: argparse.Namespace) -> None:
    scheduler = TaskScheduler(persist_path=DB_PATH)
    full_id = _resolve_id(scheduler, args.id)
    history = scheduler.get_history(full_id)
    if not history:
        console.print("[dim]No execution history yet.[/]")
        return

    table = Table(title=f"History for [cyan]{full_id[:8]}[/]", box=box.SIMPLE_HEAD)
    table.add_column("Attempt", justify="right")
    table.add_column("Status")
    table.add_column("Started (UTC)")
    table.add_column("Duration")
    table.add_column("Output / Error", overflow="fold")

    for r in history[-20:]:
        sc = _status_colour(r["status"])
        dur = ""
        if r["started_at"] and r["ended_at"]:
            from datetime import datetime as dt
            start = dt.fromisoformat(r["started_at"])
            end   = dt.fromisoformat(r["ended_at"])
            dur   = f"{(end - start).total_seconds():.3f}s"
        table.add_row(
            str(r["attempt"]),
            f"[{sc}]{r['status']}[/]",
            r["started_at"][:19] if r["started_at"] else "-",
            dur,
            r.get("output") or r.get("error") or "-",
        )
    console.print(table)


def cmd_run(args: argparse.Namespace) -> None:
    """One-shot immediate execution (does NOT require scheduler to be running)."""
    scheduler = TaskScheduler(persist_path=DB_PATH)
    full_id = _resolve_id(scheduler, args.id)

    async def _run():
        result = await scheduler.run_now(full_id)
        if result is None:
            console.print(f"[red]Task not found:[/] {args.id}")
            return
        sc = _status_colour(result.status.value)
        console.print(f"[{sc}]{result.status.value}[/] — took {result.duration_seconds:.3f}s")
        if result.output:
            console.print(f"[dim]Output:[/] {result.output}")
        if result.error:
            console.print(f"[red]Error:[/]\n{result.error}")

    asyncio.run(_run())


def cmd_start(args: argparse.Namespace) -> None:
    """Start the live scheduler — runs until Ctrl+C."""
    console.rule("[bold cyan]Task Scheduler — Live Mode[/]")

    results_log = []

    def on_result(result):
        results_log.append(result)

    scheduler = TaskScheduler(persist_path=DB_PATH, on_result=on_result)

    async def _run():
        try:
            await scheduler.start()
        except asyncio.CancelledError:
            pass

    async def _live():
        task = asyncio.create_task(_run())
        try:
            with Live(console=console, refresh_per_second=2) as live:
                while True:
                    live.update(_tasks_table(scheduler))
                    await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            pass
        scheduler.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    try:
        asyncio.run(_live())
    except KeyboardInterrupt:
        pass

    console.print("\n[bold]Scheduler stopped.[/]")
    if results_log:
        console.print(f"[dim]{len(results_log)} total executions[/]")


# ---------------------------------------------------------------------------
# ID resolution
# ---------------------------------------------------------------------------

def _resolve_id(scheduler: TaskScheduler, partial_id: str) -> str:
    """Allow short (8-char) IDs as well as full UUIDs."""
    if len(partial_id) == 36:
        return partial_id
    for task in scheduler.list_tasks():
        if task.id.startswith(partial_id):
            return task.id
    return partial_id  # fall-through — let the caller handle not-found


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task_scheduler",
        description="Cron-like Task Scheduler with Priorities",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Register a new task")
    p_add.add_argument("--name",     required=True, help="Human-readable task name")
    p_add.add_argument("--cron",     required=True, help='Cron expression e.g. "*/5 * * * * *" or @daily')
    p_add.add_argument("--priority", default="NORMAL",
                       choices=["CRITICAL", "HIGH", "NORMAL", "LOW"],
                       help="Execution priority")
    p_add.add_argument("--retries",  type=int, default=0, help="Retry count on failure")
    p_add.add_argument("--timeout",  type=float, default=None, help="Timeout in seconds")
    p_add.add_argument("--tags",     default="", help="Comma-separated tags")

    # list
    sub.add_parser("list", help="List all tasks")

    # remove / pause / resume
    for cmd in ("remove", "pause", "resume"):
        p = sub.add_parser(cmd, help=f"{cmd.capitalize()} a task")
        p.add_argument("--id", required=True, help="Task ID (full or 8-char prefix)")

    # history
    p_hist = sub.add_parser("history", help="Show execution history")
    p_hist.add_argument("--id", required=True)

    # run
    p_run = sub.add_parser("run", help="One-shot immediate execution")
    p_run.add_argument("--id", required=True)

    # start
    sub.add_parser("start", help="Start the live scheduler (Ctrl+C to stop)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "add"    : cmd_add,
        "list"   : cmd_list,
        "remove" : cmd_remove,
        "pause"  : cmd_pause,
        "resume" : cmd_resume,
        "history": cmd_history,
        "run"    : cmd_run,
        "start"  : cmd_start,
    }

    if args.command not in dispatch:
        parser.print_help()
        sys.exit(0)

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
