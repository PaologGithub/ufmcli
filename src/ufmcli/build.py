import tomllib
from contextlib import chdir

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

from ufmcli.setup import setup_assets
from ufmcli.state import AppState

PRC_DATA = '''
load-display pandagles2
aux-display pandagles

notify-level info
gl-debug true

android-app-id %s
'''

def build_project(state: AppState, console: Console):
    with open(state.paths.settings_path, "rb") as file:
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

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            setup_assets(state.paths.project_path / "assets", progress)

    with chdir(state.paths.project_path):
        try:
            setup(
                script_name="",
                script_args=["bdist_apps"],

                name=app_name_set,
                version=app_version,

                options={
                    "build_apps": {
                        "application_id": app_id,
                        "android_version_code": app_vercode,
                        "platforms": app_platforms,  # type: ignore

                        "gui_apps": {
                            app_name: app_pyfile
                        },

                        "plugins": [
                            # Use of pandagles2/pandagles instead of pandagl
                            "pandagles2",
                            "pandagles",
                            "p3openal_audio",
                        ],

                        "include_patterns": app_includes,
                        "extra_prc_data": prc,
                        "icons": {"*": app_icon}
                    }
                },

                classifiers=app_classifiers
            )
        except SystemExit as e:
            console.print(f"[red]:cross_mark:[/] Build failed: {e}")
            raise typer.Exit(code=1)