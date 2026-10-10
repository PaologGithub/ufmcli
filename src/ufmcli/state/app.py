import sys
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class PathData:
    project: Path

    @property
    def settings(self) -> Path:       return self.project / "project" / "settings.toml"
    
    @property
    def build_dir(self) -> Path:      return self.project / "build"
    @property
    def ufm_build_dir(self) -> Path:  return self.build_dir / "ufmcli"
    @property
    def bundletool(self) -> Path:     return self.ufm_build_dir / "bundletool.jar"

    @property
    def dist(self) -> Path:           return self.project / "dist" 

@dataclass()
class AppState:
    PANDA3D_BINARIES: ClassVar[dict[str, str]] = {
        "win32": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-win_amd64.whl",
        "linux": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-manylinux2014_x86_64.whl",
        "darwin": "https://buildbot.panda3d.org/downloads/b32d5c672441c280f7e799483d223e252cf9f797/panda3d-1.11.0.dev3788-cp313-cp313-macosx_11_0_universal2.whl"
    }

    BUNDLETOOL_BINARY: ClassVar[str] = "https://github.com/google/bundletool/releases/download/1.18.3/bundletool-all-1.18.3.jar"

    java_command = "java"
    java_version = 0

    os_name        = sys.platform
    python_version = sys.version

    paths: PathData = None # type: ignore