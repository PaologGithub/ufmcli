import json
import random
import tomllib
import zlib
from contextlib import chdir
from hashlib import file_digest
from pathlib import Path
from threading import Thread

import requests
import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from setuptools import setup

from ufmcli.check import check_or_exit
from ufmcli.helpers.java import run_jar
from ufmcli.state.app import AppState

PRC_DATA = '''
load-display pandagles2
aux-display pandagles

notify-level info
gl-debug true

android-app-id %s
'''
ASSET_GROUPS = ("ursina_assets", "game_assets")


def prepare(state: AppState):
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

def build_aab(state: AppState):
    with open(state.paths.settings, "rb") as file:
        content = tomllib.load(file)

    # [android] part
    app_id: str                 = content["android"]["id"]
    app_version: str            = content["android"]["version"]
    app_name_set: str           = content["android"]["name"]
    app_icon: str               = content["android"]["icon"]
    app_classifiers: list[str]  = content["android"]["classifiers"]
    # [application] part
    app_name: str               = content["application"]["name"]
    app_pyfile: str             = content["application"]["startfile"]
    # [build] part
    app_vercode: str            = content["build"]["vercode"]
    app_platforms: list[str]    = content["build"]["platforms"]
    app_includes: list[str]     = content["build"]["includes"]

    prc = PRC_DATA % app_id

    with chdir(state.paths.project):
        setup(
            script_name="", script_args=["bdist_apps"],
            name=app_name_set, version=app_version, classifiers=app_classifiers,

            options={
                "build_apps": {
                    "application_id": app_id,
                    "android_version_code": app_vercode,
                    "platforms": app_platforms,  # type: ignore

                    "gui_apps": {
                        app_name: app_pyfile
                    },
                    "plugins": ["pandagles2", "pandagles", "p3openal_audio"],

                    "include_patterns": app_includes,
                    "extra_prc_data": prc,
                    "icons": {"*": app_icon}
                }
            },
        )


def setup_asset(path: Path, assets_root: Path) -> dict[str, str]:
    with open(path, "rb") as f:
        digest = file_digest(f, "sha256")
    return {
        "dir": path.relative_to(assets_root).as_posix(),
        "sha": digest.hexdigest(),
    }


def setup_assets(assets_root: Path, progress: Progress | None = None) -> None:
    files = {
        group: sorted(p for p in (assets_root / group).rglob("*") if p.is_file())
        for group in ASSET_GROUPS
    }
    total = sum(len(v) for v in files.values())
    task = progress.add_task("Hashing assets", total=total) if progress else None

    generated: dict[str, dict[str, dict[str, str]]] = {}
    for group, paths in files.items():
        entries: dict[str, dict[str, str]] = {}
        for path in paths:
            name = path.name.replace(".", "_") + "-" + str(random.randint(0, 100))
            entries[name] = setup_asset(path, assets_root)
            if progress and task is not None:
                progress.advance(task)
        generated[group] = entries

    json_data = json.dumps(generated, indent=4, sort_keys=True).encode("utf-8")
    (assets_root / "assets.gen").write_bytes(zlib.compress(json_data))
    (assets_root / "assets_DEBUG.json").write_bytes(json_data)

def build_command(
    state:        AppState,
    console:      Console,

    skip_checks:  bool
) -> None:
    """Build the android app"""
    if not skip_checks:
        check_or_exit(state, console, interactive=True)
    prepare(state)

    with console.status("Building AAB"):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            setup_assets(state.paths.project / "assets", progress)
        try:
            thread = Thread(target=lambda: build_aab(state))
            thread.start()
            thread.join()
        except SystemExit as e:
            console.print(f"[red]:cross_mark:[/] Build failed: {e}")
            raise typer.Exit(code=1)

    with console.status("Building APKs"):
        dist_path = state.paths.dist

        apks_path = dist_path / "app.apks"
        if apks_path.exists(): apks_path.unlink()
        
        run_jar(state, state.paths.bundletool, ["build-apks", "--bundle", dist_path / "*.aab", "--output", apks_path])
        console.print(f"[green]:white_check_mark:[/] Built {dist_path / "app.apks"}")