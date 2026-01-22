import os
from pathlib import Path
import typer
from dotenv import load_dotenv
from rich import print

from reliquary.graph.workflow import build_graph, new_state
from reliquary.storage.run_store import write_json
from reliquary.schemas.state import WorkItemState
from reliquary.schemas.delivery import DeliveryConfig

app = typer.Typer(add_completion=False)

@app.command()
def run(
    repo: str = typer.Option(..., help="Path to target repo (e.g., ..\\reliquary-demo-repo)"),
    task: str = typer.Option(..., help="Task request in natural language"),
    delivery_mode: str = typer.Option("local_patch", help="Delivery mode: local_patch, github_pr, direct_push"),
    target_branch: str = typer.Option("main", help="Target branch for delivery"),
    github_token: str = typer.Option(None, help="GitHub token for PR creation (or set GITHUB_TOKEN env var)"),
):
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise typer.BadParameter("OPENAI_API_KEY missing. Put it in reliquary-engine/.env")

    repo_path = str(Path(repo).resolve())

    # Setup delivery config
    token = github_token or os.getenv("GITHUB_TOKEN")
    delivery_config = DeliveryConfig(
        mode=delivery_mode,
        target_branch=target_branch,
        github_token=token
    )

    state = new_state(repo_path=repo_path, task_raw=task)
    state.delivery_config = delivery_config

    graph = build_graph()
    final_dict = graph.invoke(state)
    final = WorkItemState.model_validate(final_dict)

    print("\n[bold cyan]Reliquary of Truth — Run Complete[/bold cyan]")
    print(f"[bold]Work Item:[/bold] {final.work_item_id}")
    print(f"[bold]Status:[/bold] {final.status}")

    if final.status == "NEEDS_INFO":
        print("\n[bold yellow]Need clarification:[/bold yellow]")
        for q in final.blocked_needs:
            print(f"- {q}")

    if final.status == "BLOCKED":
        print(f"\n[bold red]Blocked:[/bold red] {final.blocked_reason}")
        for n in final.blocked_needs:
            print(f"- {n}")

    if final.status == "DELIVERED":
        print("\n[bold green]Delivered with proof[/bold green]")
        print(f"- Tests run count: {len(final.evidence.test_runs)}")
        if final.evidence.test_runs:
            tr = final.evidence.test_runs[-1]
            print(f"- Last test exit code: {tr.exit_code}")
            print(f"- stdout: {tr.stdout_path}")
            print(f"- stderr: {tr.stderr_path}")

        if final.delivery_result:
            print(f"\n[bold cyan]Delivery Details:[/bold cyan]")
            print(f"- Mode: {final.delivery_result.mode}")
            print(f"- Status: {final.delivery_result.status}")
            if final.delivery_result.pr_url:
                print(f"- PR URL: {final.delivery_result.pr_url}")
            if final.delivery_result.patch_bundle_path:
                print(f"- Patch: {final.delivery_result.patch_bundle_path}")
            if final.delivery_result.proof_manifest_path:
                print(f"- Proof Bundle: {final.delivery_result.proof_manifest_path}")
            if final.delivery_result.error_message:
                print(f"- Error: {final.delivery_result.error_message}")

    Path("runs").mkdir(exist_ok=True)
    write_json(f"runs\\final_state_{final.work_item_id}.json", final.model_dump())


@app.command()
def query(
    repo: str = typer.Option(None, help="Filter by repository path"),
    status: str = typer.Option(None, help="Filter by status (DELIVERED, BLOCKED, etc.)"),
    limit: int = typer.Option(10, help="Maximum results to return"),
):
    """Query past runs from memory."""
    from reliquary.memory.store import query_runs

    repo_name = os.path.basename(repo) if repo else None
    runs = query_runs(repo_name=repo_name, status=status, limit=limit)

    if not runs:
        print("[yellow]No runs found matching criteria[/yellow]")
        return

    print(f"\n[bold cyan]Found {len(runs)} runs:[/bold cyan]\n")
    for run in runs:
        status_color = "green" if run.final_status == "DELIVERED" else "red"
        print(f"[{status_color}]{run.final_status}[/{status_color}] {run.work_item_id}: {run.ticket_title}")
        print(f"  Repo: {run.repo_name} | Attempts: {run.implement_attempts} | Completed: {run.completed_at}")
        if run.failure_mode:
            print(f"  Failure: {run.failure_mode}")
        print()


@app.command()
def stats():
    """Show aggregate statistics from memory."""
    from reliquary.memory.store import get_stats

    stats_data = get_stats()

    print("\n[bold cyan]Reliquary Memory Statistics[/bold cyan]\n")
    print(f"Total Runs: {stats_data['total_runs']}")
    print(f"Successful Runs: {stats_data['successful_runs']}")
    print(f"Success Rate: {stats_data['success_rate']:.1f}%")
    print(f"Average Attempts: {stats_data['avg_attempts']}")

    if stats_data['failure_modes']:
        print("\n[bold]Failure Modes:[/bold]")
        for mode, count in stats_data['failure_modes'].items():
            print(f"  {mode}: {count}")


if __name__ == "__main__":
    app()
