import sys
from importlib.util import find_spec

import colorama

RED   = colorama.Fore.RED
LRED  = colorama.Fore.LIGHTRED_EX
PINK  = colorama.Fore.LIGHTMAGENTA_EX
RESET = colorama.Fore.RESET

PANDA3D_BINARIES = {
    "win32": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-win_amd64.whl",
    "linux": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-manylinux2014_x86_64.whl",
    "darwin": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-macosx_11_0_universal2.whl"
}

# Helpers
def panic(message: str, tips: list[str | None] | None = None):
    """Panic the ufmcli with the message"""
    print(f"{RED}{message}{RESET}")
    if tips is not None:
        [print(f"{LRED}> {PINK}{tip}{RESET}") for tip in tips if tip is not None]

    sys.exit(1)
def has_module(name: str) -> bool:
    try:
        return find_spec(name) is not None
    except ModuleNotFoundError:
        return False

def main() -> None:
    # Check python version == 3.13
    if sys.version_info[:2] != (3, 13):
        panic(
            "Python interpreter should only be 3.13",
            [f"Replace Python {sys.version} with Py3.13"]
        )

    # Python dependency check
    if not has_module("panda3d"):
        panda3d_binary_tip = PANDA3D_BINARIES.get(sys.platform)
        panic(
            "Panda3D wasn't found",
            [
                "Install panda3d on your python environment" + (f"; for platform {sys.platform}, run: " if panda3d_binary_tip else ""),
                f"pip install {panda3d_binary_tip}" if panda3d_binary_tip else None
            ]
        )
    if not has_module("google.protobuf"):
        panic("Protobuf isn't installed", ["To install protobuf, run: ", "pip install protobuf===3.20.0"])
