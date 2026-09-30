# checks.py
import sys
from dataclasses import dataclass
from enum import Enum, auto

import questionary
import typer
from rich.console import Console

from ufmcli.helpers import get_java_major, has_module
from ufmcli.state import AppState

MIN_JAVA = 8


class CheckProblem(Enum):
    NO_VALID_INTERPRETER = auto()
    MISSING_PANDA3D = auto()
    MISSING_PROTOBUF = auto()
    NO_VALID_JAVA = auto()


@dataclass(frozen=True)
class Problem:
    kind: CheckProblem
    message: str
    hints: tuple[str, ...] = ()


def run_checks(state: AppState) -> list[Problem]:
    problems: list[Problem] = []

    # Python version
    if sys.version_info[:2] != (3, 13):
        problems.append(Problem(
            CheckProblem.NO_VALID_INTERPRETER,
            "Python interpreter should only be 3.13",
            (f"Replace Python {sys.version} with Py3.13",),
        ))

    # Python dependencies
    if not has_module("panda3d"):
        binary = state.PANDA3D_BINARIES.get(state.os_name)
        hints = ("Install panda3d in your Python environment",)
        if binary:
            hints += (f"For platform {state.os_name}, run: pip install {binary}",)
        problems.append(Problem(CheckProblem.MISSING_PANDA3D, "Panda3D wasn't found", hints))

    if not has_module("google.protobuf"):
        problems.append(Problem(
            CheckProblem.MISSING_PROTOBUF,
            "Protobuf isn't installed",
            ("To install protobuf, run: pip install protobuf==3.20.0",),
        ))

    # Java
    version = get_java_major(state.java_command)
    if version is None or version < MIN_JAVA:
        problems.append(Problem(
            CheckProblem.NO_VALID_JAVA,
            "No valid java found",
            ("Select a java interpreter", f"Install java >= {MIN_JAVA}"),
        ))
    else:
        state.java_version = version

    return problems

def fix_java(state: AppState, console: Console) -> bool:
    """Resolve missing java, returns True if resolved"""
    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                "Select a java interpreter",
                "Install java manually",
                "Automatically install java",
            ],
        ).ask()

        match choice:
            case "Select a java interpreter":
                path = questionary.path("Enter a java interpreter >").ask()
                if path:
                    state.java_command = path
                version = get_java_major(state.java_command)
                if version is not None and version >= MIN_JAVA:
                    state.java_version = version
                    return True
                console.print(f"[red]X[/] That isn't a valid java >= {MIN_JAVA}")
            case "Automatically install java":
                console.print("[yellow]Automatic installation isn't implemented yet[/]")
            case _:
                return False

def report(problems: list[Problem], console: Console) -> None:
    for p in problems:
        console.print(f"[red]:cross_mark:[/] {p.message}")
        for hint in p.hints:
            console.print(f"    [dim]->[/] {hint}")


def check_or_exit(state, console: Console, interactive: bool = True) -> None:
    problems = run_checks(state)
    if not problems:
        return

    report(problems, console)

    if interactive and any(p.kind is CheckProblem.NO_VALID_JAVA for p in problems) and fix_java(state, console):
        problems = [p for p in problems if p.kind is not CheckProblem.NO_VALID_JAVA]

    if problems:
        raise typer.Exit(code=1)