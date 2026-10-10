import requests
from rich.console import Console
from rich.progress import Progress

from ufmcli.helpers.java import run_jar
from ufmcli.state.app import AppState


def install_command(
    state: AppState,
    console: Console
) -> None:
    """Installs the android app"""

    state.paths.build_dir.mkdir(exist_ok=True)
    state.paths.ufm_build_dir.mkdir(exist_ok=True)

    if not state.paths.bundletool.exists():
        response = requests.get(state.BUNDLETOOL_BINARY, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024

        with Progress() as progress, open(state.paths.bundletool, "wb") as file:
            task = progress.add_task("Downloading BundleTool", total=total_size)
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    progress.update(task, advance=len(chunk))

    dist_path = state.paths.dist
    apks_path = dist_path / "app.apks"

    with console.status("Installing APKs"):
        run_jar(state, state.paths.bundletool, ["install-apks", "--apks", apks_path])
        console.print(f"[green]:white_check_mark:[/] Installed {apks_path}")