"""
demo.py — Self-contained demonstration of the Task Scheduler.

Registers 5 sample tasks with varied cron schedules and priorities,
then runs the scheduler for 35 seconds showing a live Rich dashboard.
"""
from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from scheduler import Task, Priority, CronExpression, TaskScheduler
from scheduler.models import TaskResult, TaskStatus

console = Console()
DEMO_DURATION = 35  # seconds


# ---------------------------------------------------------------------------
# Sample task callables
# ---------------------------------------------------------------------------

def health_check():
    """Simulate a health-check ping."""
    latency = random.uniform(1, 50)
    print(f"API latency: {latency:.1f}ms — OK")


def cleanup_temp_files():
    """Simulate temp-file removal."""
    count = random.randint(0, 120)
    print(f"Deleted {count} temp file(s)")


def send_report():
    """Simulate sending a report email."""
    print("Report dispatched to team@company.com")


def metric_aggregator():
    """Simulate metric aggregation — occasionally fails."""
    if random.random() < 0.25:
        raise RuntimeError("Metrics service unreachable — connection refused")
    print(f"Aggregated {random.randint(1000, 9999)} data points")


async def async_db_backup():
    """Async simulated database backup."""
    await asyncio.sleep(random.uniform(0.1, 0.3))
    size_mb = random.uniform(10, 500)
    print(f"Backup complete: {size_mb:.1f} MB written to s3://backups/")


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------

def _build_results_table(results: list[TaskResult]) -> Table:
    table = Table(
        title="[bold]Recent Executions[/]",
        box=box.SIMPLE_HEAD,
        show_header=True,
        padding=(0, 1),
    )
    table.add_column("Time",     no_wrap=True, style="dim")
    table.add_column("Task",     style="bold")
    table.add_column("Priority", no_wrap=True)
    table.add_column("Status",   no_wrap=True)
    table.add_column("Attempt",  justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Output / Error", overflow="fold")

    colours = {
        "CRITICAL": "red",
        "HIGH"    : "orange3",
        "NORMAL"  : "green",
        "LOW"     : "dim",
    }
    scolours = {
        TaskStatus.SUCCESS: "bold green",
        TaskStatus.FAILED : "bold red",
        TaskStatus.RUNNING: "bold yellow",
    }

    for r in reversed(results[-20:]):
        task_ref = r  # TaskResult
        sc = scolours.get(r.status, "white")
        dur = f"{r.duration_seconds:.3f}s" if r.duration_seconds is not None else "-"
        detail = (r.output or r.error or "").strip().split("\n")[0][:60]
        table.add_row(
            r.started_at.strftime("%H:%M:%S"),
            r.task_name,
            "-",      # priority not stored in result; cosmetic
            f"[{sc}]{r.status.value}[/]",
            str(r.attempt),
            dur,
            detail or "-",
        )
    return table


def _build_tasks_table(scheduler: TaskScheduler) -> Table:
    table = Table(
        title="[bold cyan]Scheduled Tasks[/]",
        box=box.ROUNDED,
        show_lines=True,
        highlight=True,
    )
    table.add_column("Name",      style="bold")
    table.add_column("Priority",  no_wrap=True)
    table.add_column("Cron",      style="cyan", no_wrap=True)
    table.add_column("Status",    no_wrap=True)
    table.add_column("Next Run",  no_wrap=True)

    pcolour = {
        Priority.CRITICAL: "bold red",
        Priority.HIGH    : "orange3",
        Priority.NORMAL  : "green",
        Priority.LOW     : "dim",
    }
    scolour = {
        "PENDING"  : "cyan",
        "RUNNING"  : "bold yellow",
        "SUCCESS"  : "bold green",
        "FAILED"   : "bold red",
        "PAUSED"   : "dim magenta",
    }

    for t in scheduler.list_tasks():
        pc = pcolour.get(t.priority, "white")
        sc = scolour.get(t.status.value, "white")
        nr = t.next_run.strftime("%H:%M:%S") if t.next_run else "-"
        table.add_row(
            t.name,
            f"[{pc}]{t.priority.name}[/]",
            str(t.cron),
            f"[{sc}]{t.status.value}[/]",
            nr,
        )
    return table


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

async def main() -> None:
    console.rule("[bold cyan]Task Scheduler — Live Demo[/]")
    console.print(
        f"[dim]Running for {DEMO_DURATION}s • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}[/]\n"
    )

    results: list[TaskResult] = []

    def on_result(r: TaskResult):
        results.append(r)

    scheduler = TaskScheduler(on_result=on_result)

    # Register demo tasks — all scheduled every few seconds for demo purposes
    tasks_def = [
        Task(
            name        = "Health Check",
            cron        = CronExpression("*/3 * * * * *"),  # every 3 seconds
            func        = health_check,
            priority    = Priority.CRITICAL,
            retry_count = 2,
            timeout     = 5.0,
            tags        = ["monitoring", "health"],
        ),
        Task(
            name        = "Metric Aggregator",
            cron        = CronExpression("*/5 * * * * *"),  # every 5 seconds
            func        = metric_aggregator,
            priority    = Priority.HIGH,
            retry_count = 1,
            timeout     = 8.0,
            tags        = ["metrics"],
        ),
        Task(
            name        = "DB Backup (async)",
            cron        = CronExpression("*/7 * * * * *"),  # every 7 seconds
            func        = async_db_backup,
            priority    = Priority.HIGH,
            timeout     = 10.0,
            tags        = ["backup", "database"],
        ),
        Task(
            name        = "Temp File Cleanup",
            cron        = CronExpression("*/10 * * * * *"), # every 10 seconds
            func        = cleanup_temp_files,
            priority    = Priority.NORMAL,
            tags        = ["maintenance"],
        ),
        Task(
            name        = "Send Report",
            cron        = CronExpression("*/15 * * * * *"), # every 15 seconds
            func        = send_report,
            priority    = Priority.LOW,
            tags        = ["reporting", "email"],
        ),
    ]

    for t in tasks_def:
        scheduler.add_task(t)

    start_time = time.monotonic()

    async def _run_scheduler():
        await scheduler.start()

    scheduler_task = asyncio.create_task(_run_scheduler())

    try:
        with Live(console=console, refresh_per_second=4) as live:
            while time.monotonic() - start_time < DEMO_DURATION:
                elapsed   = time.monotonic() - start_time
                remaining = DEMO_DURATION - elapsed

                layout = Layout()
                layout.split_column(
                    Layout(name="top"),
                    Layout(name="bottom"),
                )
                layout["top"].update(
                    Panel(
                        _build_tasks_table(scheduler),
                        title=f"[bold]⏱  Elapsed: {elapsed:.0f}s  |  Remaining: {remaining:.0f}s[/]",
                        border_style="cyan",
                    )
                )
                layout["bottom"].update(
                    Panel(
                        _build_results_table(results),
                        title=f"[bold]📋 Executions so far: {len(results)}[/]",
                        border_style="green",
                    )
                )
                live.update(layout)
                await asyncio.sleep(0.25)
    except KeyboardInterrupt:
        pass

    scheduler.stop()
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass

    # Final summary
    console.rule("[bold]Demo Complete[/]")
    successes = sum(1 for r in results if r.status == TaskStatus.SUCCESS)
    failures  = sum(1 for r in results if r.status == TaskStatus.FAILED)
    console.print(
        f"[bold]Total executions:[/] {len(results)}  "
        f"[green]✓ {successes} success[/]  "
        f"[red]✗ {failures} failed[/]"
    )
    console.print(_build_results_table(results))


if __name__ == "__main__":
    asyncio.run(main())
