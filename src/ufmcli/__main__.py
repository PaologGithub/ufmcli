import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ufmcli.check import check_or_exit
from ufmcli.commands.build import build_command
from ufmcli.commands.install import install_command
from ufmcli.state.app import AppState, PathData

app = typer.Typer(
    help="UrsinaForMobile CLI tool",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
ProjectDir = Annotated[
    Path,
    typer.Argument(help = "Path to the project dir", file_okay=False, resolve_path=True)
]
JavaCommand = Annotated[
    str,
    typer.Option("--java-command", envvar="UFM_JAVA", help="Path to the java executable")
]

state = AppState()
console = Console()

@app.command()
def build(
    project_dir:  ProjectDir = Path("."),
    skip_checks:  Annotated[bool, typer.Option("--skip-check", help="Skip environment checks")] = False,
    java_command: JavaCommand = "java"
) -> None:
    state.paths = PathData(project_dir)
    state.java_command = java_command
    build_command(
        state, console, skip_checks
    )

@app.command()
def check(project_dir: ProjectDir = Path("."), java_command: JavaCommand = "java") -> None:
    """Checks the environment"""
    state.paths = PathData(project_dir)
    state.java_command = java_command

    check_or_exit(state, console, interactive=False)
    console.print(f"[green]:white_check_mark:[/] Python {sys.version.split()[0]}, Java {state.java_version}")

@app.command()
def install(project_dir: ProjectDir = Path("."), java_command: JavaCommand = "java"):
    state.paths = PathData(project_dir)
    state.java_command = java_command

    install_command(state, console)

def main() -> None:
    app()

if __name__ == "__main__":
    main()