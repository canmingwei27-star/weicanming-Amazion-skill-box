#!/usr/bin/env python3
"""Safely sync Amazon skills from this repository into a Codex skills directory."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import urllib.request
import zipfile


REPOSITORY = "canmingwei27-star/weicanming-Amazion-skill-box"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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
    url = f"https://codeload.github.com/{owner}/{repo}/zip/{ref}"
    archive_path = destination / "repository.zip"
    urllib.request.urlretrieve(url, archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        safe_extract(archive, destination)
        roots = sorted({PurePosixPath(name).parts[0] for name in archive.namelist() if name})
    if len(roots) != 1:
        raise RuntimeError("Unexpected repository archive layout")
    return destination / roots[0]


def within(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if path != root.resolve() and root.resolve() not in path.parents:
        raise RuntimeError(f"Path escapes its allowed directory: {relative}")
    return path


def validate_name(name: str) -> None:
    if not NAME_RE.fullmatch(name):
        raise ValueError(f"Invalid skill name: {name}")


def manifest_entries(manifest: dict) -> list[dict]:
    if manifest.get("schema_version") != 2 or manifest.get("platform") != "amazon":
        raise RuntimeError("Expected Amazon skill manifest schema_version 2")
    router = manifest.get("router")
    skills = manifest.get("skills")
    if not isinstance(router, dict) or not isinstance(skills, list):
        raise RuntimeError("Manifest must contain router and skills entries")
    if router.get("name") != "amazon-skill-router":
        raise RuntimeError("Manifest router must be named amazon-skill-router")
    if not isinstance(manifest.get("routing_policy"), list) or not manifest["routing_policy"]:
        raise RuntimeError("Manifest must define routing_policy")
    entries = [router, *skills]
    names = set()
    for entry in entries:
        name = entry.get("name", "")
        validate_name(name)
        if name in names:
            raise RuntimeError(f"Duplicate skill name: {name}")
        names.add(name)
        if not entry.get("path") or not isinstance(entry.get("include"), list) or not entry["include"]:
            raise RuntimeError(f"Missing path or include list for {name}")
        if name != "amazon-skill-router" and not entry["path"].replace("\\", "/").startswith("skill库/"):
            raise RuntimeError(f"Child skill must be stored under skill库/: {entry['path']}")
        if name != "amazon-skill-router":
            if not entry.get("category") or not entry.get("description") or not entry.get("triggers"):
                raise RuntimeError(f"Missing routing metadata for {name}")
    return entries


def copy_entry(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def populate_skill(repo_root: Path, entry: dict, destination: Path) -> None:
    name = entry["name"]
    source_root = within(repo_root, entry["path"])
    if not source_root.is_dir():
        raise RuntimeError(f"Skill path does not exist: {entry['path']}")
    destination.mkdir(parents=True, exist_ok=True)
    for relative in entry["include"]:
        source = within(source_root, relative)
        if source != source_root and source_root not in source.parents:
            raise RuntimeError(f"Skill include escapes skill path: {relative}")
        if not source.exists():
            raise RuntimeError(f"Missing skill include: {entry['path']}/{relative}")
        copy_entry(source, destination / relative)


def sync_skill(repo_root: Path, entry: dict, target_root: Path, force: bool, backup_root: Path) -> str:
    name = entry["name"]
    target = target_root / name
    if target.exists() and not force:
        return f"SKIP existing: {name} (use --force to back up and replace)"

    stage = Path(tempfile.mkdtemp(prefix=f".{name}-", dir=target_root))
    backup = None
    try:
        populate_skill(repo_root, entry, stage)
        if target.exists():
            stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backup = backup_root / stamp / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(target, backup)
            shutil.rmtree(target)
        os.replace(stage, target)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        if backup is not None and backup.exists() and not target.exists():
            shutil.copytree(backup, target)
        raise
    return f"SYNCED: {name}"


def sync_from_repository(repo_root: Path, target_root: Path, force: bool) -> None:
    manifest_path = repo_root / "skills-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest_entries(manifest)
    target_root.mkdir(parents=True, exist_ok=True)
    backup_root = target_root / ".skill-backups"
    for entry in entries:
        print(sync_skill(repo_root, entry, target_root, force, backup_root))


def find_local_repository() -> Path | None:
    candidates = [Path.cwd(), Path(__file__).resolve().parents[1]]
    for candidate in candidates:
        if (candidate / "skills-manifest.json").is_file():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=default_target())
    parser.add_argument("--repository", default=REPOSITORY)
    parser.add_argument("--ref", default="main", help="branch, tag, or commit to download")
    parser.add_argument(
        "--source",
        choices=["auto", "local", "remote"],
        default="auto",
        help="Use the checked-out repository when available, or download the GitHub backup",
    )
    parser.add_argument("--force", action="store_true", help="Back up and replace existing skill directories")
    args = parser.parse_args()

    local_repository = find_local_repository() if args.source in {"auto", "local"} else None
    if args.source == "local" and local_repository is None:
        raise RuntimeError("Local repository not found; run from the skill-box checkout")
    if local_repository is not None:
        sync_from_repository(local_repository, args.target, args.force)
        return 0

    with tempfile.TemporaryDirectory(prefix="codex-skill-sync-") as temporary:
        repo_root = download_repository(args.repository, args.ref, Path(temporary))
        sync_from_repository(repo_root, args.target, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
