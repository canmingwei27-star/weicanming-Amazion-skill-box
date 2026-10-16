#!/usr/bin/env python3
"""Safely restore Codex skills from the Amazon skill-box GitHub backup."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.request
import zipfile


REPOSITORY = "canmingwei27-star/weicanming-Amazion-skill-box"


def default_target() -> Path:
    return Path.home() / ".codex" / "skills"


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    root = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if target != root and root not in target.parents:
            raise RuntimeError(f"Unsafe archive entry: {member.filename}")
    archive.extractall(destination)


def download_repository(repository: str, ref: str, destination: Path) -> Path:
    owner, repo = repository.split("/", 1)
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{ref}"
    archive_path = destination / "repository.zip"
    urllib.request.urlretrieve(url, archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        safe_extract(archive, destination)
        roots = sorted({PurePosixPath(name).parts[0] for name in archive.namelist() if name})
    if len(roots) != 1:
        raise RuntimeError("Unexpected repository archive layout")
    return destination / roots[0]


def validate_name(name: str) -> None:
    if not name or len(name) > 64 or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in name):
        raise ValueError(f"Invalid skill name: {name}")


def copy_entry(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def sync_skill(repo_root: Path, entry: dict, target_root: Path, force: bool, backup_root: Path) -> str:
    name = entry["name"]
    validate_name(name)
    source_root = (repo_root / entry["path"]).resolve()
    target = target_root / name
    if not source_root.is_dir():
        raise RuntimeError(f"Skill path does not exist: {entry['path']}")

    if target.exists() and not force:
        return f"SKIP existing: {name} (use --force to update; no files changed)"

    if target.exists() and force:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = backup_root / stamp / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(target, backup)

    target.mkdir(parents=True, exist_ok=True)
    includes = entry.get("include")
    if includes:
        for relative in includes:
            source = (source_root / relative).resolve()
            if source != source_root and source_root not in source.parents:
                raise RuntimeError(f"Skill include escapes skill path: {relative}")
            if not source.exists():
                raise RuntimeError(f"Missing skill include: {relative}")
            copy_entry(source, target / relative)
    else:
        for child in source_root.iterdir():
            copy_entry(child, target / child.name)
    return f"SYNCED: {name}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=default_target())
    parser.add_argument("--repository", default=REPOSITORY)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--force", action="store_true", help="Back up and update existing skills")
    args = parser.parse_args()

    args.target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-skill-sync-") as temporary:
        repo_root = download_repository(args.repository, args.ref, Path(temporary))
        manifest_path = repo_root / "skills-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("platform") != "amazon":
            raise RuntimeError("This skill box is restricted to the Amazon platform")
        backup_root = args.target / ".skill-backups"
        for entry in manifest.get("skills", []):
            print(sync_skill(repo_root, entry, args.target, args.force, backup_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

