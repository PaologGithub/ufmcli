import json
import random
import zlib
from hashlib import file_digest
from pathlib import Path

from rich.progress import Progress

ASSET_GROUPS = ("ursina_assets", "game_assets")


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