import re
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path

import colorama

RED   = colorama.Fore.RED
LRED  = colorama.Fore.LIGHTRED_EX
PINK  = colorama.Fore.LIGHTMAGENTA_EX
RESET = colorama.Fore.RESET

def error(message: str, tips: list[str | None] | None = None):
    print(f"{RED}{message}{RESET}")
    if tips is not None:
        [print(f"{LRED}> {PINK}{tip}{RESET}") for tip in tips if tip is not None]

def panic(message: str, tips: list[str | None] | None = None):
    error(message, tips)
    sys.exit(1)

def has_module(name: str) -> bool:
    try:
        return find_spec(name) is not None
    except ModuleNotFoundError:
        return False
    
def get_java_major(jvm: str | None = None) -> int | None:
    java = shutil.which(jvm if jvm else "java")
    if java is None:
        return None
    
    try:
        result = subprocess.run([java, "-version"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    
    match = re.search(r'version "(\d+)(?:\.(\d+))?', result.stderr)
    if not match:
        return None
    
    major = int(match.group(1))
    
    return int(match.group(2)) if major == 1 and match.group(2) else major

@dataclass(frozen=True)
class Arguments:
    project_dir: Path

def parse_args() -> Arguments:
    parser = ArgumentParser(
        prog="ufmcli",
        description="UrsinaForMobile build tool",
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        type=Path,
        help="Path to the project directory (default: current directory)",
    )
    args = parser.parse_args()

    return Arguments(args.project_dir)