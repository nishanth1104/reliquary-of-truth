import os
from pathlib import Path
import typer
from dotenv import load_dotenv
from rich import print

from reliquary.graph.workflow import build_graph, new_state
from reliquary.storage.run_store import write_json
from reliquary.schemas.state import WorkItemState

app = typer.Typer(add_completion=False)

@app.command()
def run(
    repo: str = typer.Option(..., help="Path to target repo (e.g., ..\\reliquary-demo-repo)"),
    task: str = typer.Option(..., help="Task request in natural language"),
):
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise typer.BadParameter("OPENAI_API_KEY missing. Put it in reliquary-engine/.env")

    repo_path = str(Path(repo).resolve())
    state = new_state(repo_path=repo_path, task_raw=task)

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

    Path("runs").mkdir(exist_ok=True)
    write_json(f"runs\\final_state_{final.work_item_id}.json", final.model_dump())

if __name__ == "__main__":
    app()
