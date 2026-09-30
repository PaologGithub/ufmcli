import subprocess
import sys
from pathlib import Path
from typing import Annotated

import requests
import typer
from rich.console import Console
from rich.progress import Progress

from ufmcli.build import build_project
from ufmcli.check import check_or_exit
from ufmcli.state import AppState

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
    """Build the android app"""
    state.java_command = java_command
    if not skip_checks:
        check_or_exit(state, console, interactive=True)

    state.paths.from_path(project_dir)
    state.paths.build_dir.mkdir(exist_ok=True)
    state.paths.build_cli_dir.mkdir(exist_ok=True)

    if not state.paths.bundletool_path.exists():
        response = requests.get(state.BUNDLETOOL_BINARY, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024

        with Progress() as progress, open(state.paths.bundletool_path, "wb") as file:
            task = progress.add_task("Downloading BundleTool", total=total_size)
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    progress.update(task, advance=len(chunk))

    with console.status("Building"):
        build_project(state, console)
        dist_path = state.paths.project_path / "dist"
        subprocess.run(f"{state.java_command} -jar {state.paths.bundletool_path} build-apks --bundle {dist_path / "*.aab"} --output {dist_path / "app.apks"}", check=False)
        console.print(f"[green]:white_check_mark:[/] Built {dist_path / "app.apks"}")

@app.command()
def check(project_dir: ProjectDir = Path("."), java_command: JavaCommand = "java") -> None:
    """Checks the environment"""
    state.java_command = java_command
    check_or_exit(state, console, interactive=False)
    console.print(f"[green]:white_check_mark:[/] Python {sys.version.split()[0]}, Java {state.java_version}")