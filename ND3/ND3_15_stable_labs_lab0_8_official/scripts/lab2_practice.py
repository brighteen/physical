#!/usr/bin/env python3
"""Lab 2 practice: inspect, save, backup, delete, and restore SLAM map files."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil

import numpy as np
import yaml

from lab_common import ROOT, print_status, quote_command, run_stream, use_repo_root
from map_utils import load_map


MAPS_DIR = ROOT / "maps"


def repo_path(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def is_inside_maps(path: Path) -> bool:
    resolved = path.resolve()
    maps_dir = MAPS_DIR.resolve()
    return resolved == maps_dir or maps_dir in resolved.parents


def map_files_from_yaml(map_yaml: Path) -> list[Path]:
    files = [map_yaml]
    try:
        with map_yaml.open("r", encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}
        image = meta.get("image")
        if image:
            files.append((map_yaml.parent / image).resolve())
    except Exception:
        fallback = map_yaml.with_suffix(".pgm")
        if fallback.exists():
            files.append(fallback)

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def inspect_map(map_yaml: Path) -> int:
    if not map_yaml.exists():
        print_status(False, "map yaml", f"not found: {map_yaml}")
        return 1

    gmap = load_map(map_yaml)
    free = int(np.count_nonzero(gmap.free_mask))
    total = int(gmap.free_mask.size)
    occupied_or_unknown = total - free
    free_percent = 100.0 * free / total if total else 0.0

    print_status(True, "map yaml", str(gmap.yaml_path))
    print_status(True, "map image", str(gmap.image_path))
    print(f"resolution_m_per_cell: {gmap.resolution}")
    print(f"origin: {gmap.origin}")
    print(f"size_cells: width={gmap.width}, height={gmap.height}")
    print(f"free_cells: {free} ({free_percent:.1f}%)")
    print(f"occupied_or_unknown_cells: {occupied_or_unknown}")
    return 0


def list_maps() -> int:
    yaml_files = sorted(MAPS_DIR.glob("*.yaml"))
    if not yaml_files:
        print_status(False, "maps/*.yaml", "no map YAML files found")
        return 1

    for yaml_path in yaml_files:
        try:
            gmap = load_map(yaml_path)
            free = int(np.count_nonzero(gmap.free_mask))
            total = int(gmap.free_mask.size)
            free_percent = 100.0 * free / total if total else 0.0
            print(
                f"{yaml_path}: image={gmap.image_path.name}, "
                f"size={gmap.width}x{gmap.height}, resolution={gmap.resolution}, "
                f"free={free_percent:.1f}%"
            )
        except Exception as exc:
            print_status(False, str(yaml_path), str(exc))
    return 0


def backup_map(map_yaml: Path, backup_dir: Path | None = None, dry_run: bool = False) -> int:
    if not map_yaml.exists():
        print_status(False, "map yaml", f"not found: {map_yaml}")
        return 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = backup_dir or (MAPS_DIR / "backups" / f"{map_yaml.stem}_{stamp}")
    files = map_files_from_yaml(map_yaml)

    print(f"backup_dir: {out_dir}")
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
    missing = 0
    for path in files:
        if not path.exists():
            print_status(False, f"backup source {path.name}", "missing")
            missing += 1
            continue
        dst = out_dir / path.name
        if dry_run:
            print(f"[DRY-RUN] copy {path} -> {dst}")
        else:
            shutil.copy2(path, dst)
            print_status(True, f"copied {path.name}", str(dst))
    return 0 if missing == 0 else 1


def delete_map(map_yaml: Path, confirm_delete: bool, make_backup: bool, dry_run: bool) -> int:
    if not map_yaml.exists():
        print_status(False, "map yaml", f"not found: {map_yaml}")
        return 1
    if not is_inside_maps(map_yaml):
        print_status(False, "safe delete scope", "only files under maps/ can be deleted by this practice script")
        return 1

    files = map_files_from_yaml(map_yaml)
    print("Files selected for deletion:")
    for path in files:
        print(f"- {path} {'(exists)' if path.exists() else '(missing)'}")

    if not confirm_delete:
        print("\nDeletion is blocked. Re-run with --confirm-delete after checking the file list.")
        print("Example:")
        print(f"python3 scripts/lab2_practice.py --action delete-map --map {map_yaml.relative_to(ROOT)} --confirm-delete")
        return 2

    if make_backup:
        code = backup_map(map_yaml, dry_run=dry_run)
        if code != 0:
            print("Backup failed, so deletion stopped.")
            return code

    failures = 0
    for path in files:
        if not path.exists():
            continue
        if not is_inside_maps(path):
            print_status(False, f"delete {path.name}", "outside maps/")
            failures += 1
            continue
        if dry_run:
            print(f"[DRY-RUN] delete {path}")
            continue
        path.unlink()
        print_status(True, f"deleted {path.name}", str(path))
    return 0 if failures == 0 else 1


def restore_map(backup_dir: Path, overwrite: bool, dry_run: bool) -> int:
    if not backup_dir.exists():
        print_status(False, "backup dir", f"not found: {backup_dir}")
        return 1
    yaml_files = sorted(backup_dir.glob("*.yaml"))
    if not yaml_files:
        print_status(False, "backup yaml", "no YAML file found in backup dir")
        return 1

    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in backup_dir.iterdir() if path.suffix.lower() in {".yaml", ".pgm", ".png"})
    failures = 0
    for src in files:
        dst = MAPS_DIR / src.name
        if dst.exists() and not overwrite:
            print_status(False, f"restore {src.name}", "destination exists; add --overwrite to replace")
            failures += 1
            continue
        if dry_run:
            print(f"[DRY-RUN] copy {src} -> {dst}")
        else:
            shutil.copy2(src, dst)
            print_status(True, f"restored {src.name}", str(dst))
    return 0 if failures == 0 else 1


def print_commands(prefix: str) -> None:
    commands = [
        ["source", "scripts/env.sh"],
        ["./scripts/lab1_start_gazebo.sh"],
        ["./scripts/lab2_start_slam_toolbox.sh"],
        ["./scripts/lab2_start_rviz_safe.sh"],
        ["./scripts/lab2_teleop.sh"],
        ["./scripts/lab2_save_map.sh", prefix],
        ["python3", "scripts/lab2_practice.py", "--action", "inspect-map", "--map", f"{prefix}.yaml"],
        ["python3", "scripts/lab2_practice.py", "--action", "list-maps"],
        ["python3", "scripts/lab2_practice.py", "--action", "backup-map", "--map", f"{prefix}.yaml"],
        ["python3", "scripts/lab2_practice.py", "--action", "delete-map", "--map", f"{prefix}.yaml", "--confirm-delete"],
    ]
    for command in commands:
        print(quote_command(command))


def save_map(prefix: str, dry_run: bool) -> int:
    out = ROOT / prefix
    out.parent.mkdir(parents=True, exist_ok=True)
    return run_stream(
        ["ros2", "run", "nav2_map_server", "map_saver_cli", "-f", str(out)],
        dry_run=dry_run,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--action",
        choices=["inspect-map", "list-maps", "save-map", "backup-map", "delete-map", "restore-map", "commands"],
        default="inspect-map",
    )
    parser.add_argument("--map", default="maps/lab_map.yaml")
    parser.add_argument("--prefix", default="maps/lab_map")
    parser.add_argument("--backup-dir")
    parser.add_argument("--confirm-delete", action="store_true")
    parser.add_argument("--no-backup", action="store_true", help="Delete without making a timestamped backup first.")
    parser.add_argument("--overwrite", action="store_true", help="Allow restore-map to replace existing files.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.action == "commands":
        print_commands(args.prefix)
    elif args.action == "list-maps":
        raise SystemExit(list_maps())
    elif args.action == "save-map":
        raise SystemExit(save_map(args.prefix, args.dry_run))
    elif args.action == "backup-map":
        raise SystemExit(backup_map(repo_path(args.map), repo_path(args.backup_dir) if args.backup_dir else None, args.dry_run))
    elif args.action == "delete-map":
        raise SystemExit(delete_map(repo_path(args.map), args.confirm_delete, not args.no_backup, args.dry_run))
    elif args.action == "restore-map":
        if not args.backup_dir:
            raise SystemExit("--backup-dir is required for restore-map")
        raise SystemExit(restore_map(repo_path(args.backup_dir), args.overwrite, args.dry_run))
    else:
        raise SystemExit(inspect_map(repo_path(args.map)))


if __name__ == "__main__":
    main()
