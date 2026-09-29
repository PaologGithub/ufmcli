import sys

import questionary
import requests
from tqdm import tqdm

from ufmcli.helpers import error, get_java_major, has_module, panic, parse_args

PANDA3D_BINARIES = {
    "win32": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-win_amd64.whl",
    "linux": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-manylinux2014_x86_64.whl",
    "darwin": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-macosx_11_0_universal2.whl"
}
BUNDLETOOL_BINARY = "https://github.com/google/bundletool/releases/download/1.18.3/bundletool-all-1.18.3.jar"

# Informations
osver = sys.platform
java  = ""

def main() -> None:
    args = parse_args()
    
    build_dir = args.project_dir / "build"
    build_cli_dir = build_dir / "ufmcli"
    bundletool_path = build_cli_dir / "bundletool.jar"

    toml_path = args.project_dir / "project" / "settings.toml"

    if not toml_path.exists():
        panic(f"{args.project_dir} is not a valid UfM project", ["Choose a path using ufmcli <project_dir>"])


    # Check python version == 3.13
    if sys.version_info[:2] != (3, 13):
        panic(
            "Python interpreter should only be 3.13",
            [f"Replace Python {sys.version} with Py3.13"]
        )
    print(f"Using Python {sys.version}")

    # Python dependency check
    if not has_module("panda3d"):
        panda3d_binary_tip = PANDA3D_BINARIES.get(osver)
        panic(
            "Panda3D wasn't found",
            [
                "Install panda3d on your python environment" + (f"; for platform {osver}, run: " if panda3d_binary_tip else ""),
                f"pip install {panda3d_binary_tip}" if panda3d_binary_tip else None
            ]
        )
    if not has_module("google.protobuf"):
        panic("Protobuf isn't installed", ["To install protobuf, run: ", "pip install protobuf===3.20.0"])

    # Android dependencies
    java = get_java_major("java")
    while java is None or java < 8:
        error("No valid java found", ["Select a java version", "Install java >= 8"])
        choice = questionary.select(
            "What do you want to do?",
            choices = [
                "Select a java interpreter",
                "Install java manually",
                "Automatically install java"
            ]
        ).ask()
        match choice:
            case "Select a java interpreter":
                java = get_java_major(questionary.path("Enter a java interpreter >").ask())
            case "Install java manually":
                panic("No valid java found", ["Install java >= 8"])
            case "Automatically install java":
                # TODO: Implement this
                panic("Java automatic implementation isn't implemented yet")
    print(f"Using Java {java}")

    build_dir.mkdir(exist_ok=True)
    build_cli_dir.mkdir(exist_ok=True)
    if not bundletool_path.exists():
        response = requests.get(BUNDLETOOL_BINARY, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading bundletool") as progress_bar, open(bundletool_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))