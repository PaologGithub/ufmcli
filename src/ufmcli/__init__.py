import sys

import questionary
import requests
from tqdm import tqdm

from ufmcli.helpers import error, get_java_major, has_module, panic, parse_args
from ufmcli.state import AppState

state = AppState()

def main() -> None:
    args = parse_args()
    state.paths.from_path(args.project_dir)

    if not state.paths.settings_path.exists():
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
        panda3d_binary_tip = state.PANDA3D_BINARIES.get(state.os_name)
        panic(
            "Panda3D wasn't found",
            [
                "Install panda3d on your python environment" + (f"; for platform {state.os_name}, run: " if panda3d_binary_tip else ""),
                f"pip install {panda3d_binary_tip}" if panda3d_binary_tip else None
            ]
        )
    if not has_module("google.protobuf"):
        panic("Protobuf isn't installed", ["To install protobuf, run: ", "pip install protobuf===3.20.0"])

    # Android dependencies
    state.java_version = get_java_major(state.java_command)
    while state.java_version < 8:
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
                state.java_command = questionary.path("Enter a java interpreter >").ask()
                state.java_version = get_java_major(state.java_command)
            case "Install java manually":
                panic("No valid java found", ["Install java >= 8"])
            case "Automatically install java":
                # TODO: Implement this
                panic("Java automatic implementation isn't implemented yet")
    print(f"Using Java {state.java_version}")

    state.paths.build_dir.mkdir(exist_ok=True)
    state.paths.build_cli_dir.mkdir(exist_ok=True)

    if not state.paths.bundletool_path.exists():
        response = requests.get(state.BUNDLETOOL_BINARY, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading bundletool") as progress_bar, open(state.paths.bundletool_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))