import re
import shutil
import subprocess
from importlib.util import find_spec
from typing import Any

from ufmcli.state.app import AppState


def has_module(name: str) -> bool:
    try:
        return find_spec(name) is not None
    except ModuleNotFoundError:
        return False
    
def get_java_major(jvm: str | None = None) -> int:
    java = shutil.which(jvm if jvm else "java")
    if java is None:
        return 0
    
    try:
        result = subprocess.run([java, "-version"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return 0
    
    match = re.search(r'version "(\d+)(?:\.(\d+))?', result.stderr)
    if not match:
        return 0
    
    major = int(match.group(1))
    
    return int(match.group(2)) if major == 1 and match.group(2) else major

def run_jar(state: AppState, jar_path: Any, arguments: list[Any]):
    subprocess.run([state.java_command, "-jar", jar_path, *arguments], check=True)