#!/usr/bin/env python3
"""Lab 6 practice: spawn/delete an obstacle and clear Nav2 costmaps."""
from __future__ import annotations

import argparse
import re
import time
from pathlib import Path
from xml.sax.saxutils import escape

from lab_common import ROOT, print_status, quote_command, ros2, run_stream, use_repo_root


CLEAR_SERVICES = [
    "/local_costmap/clear_entirely_local_costmap",
    "/global_costmap/clear_entirely_global_costmap",
]

DELETE_SERVICES = ["/delete_entity", "/gazebo/delete_entity"]
GENERATED_MODEL_DIR = Path("/tmp/nd3_lab_models")


def require_positive(label: str, value: float) -> None:
    if value <= 0:
        raise SystemExit(f"{label} must be greater than 0. Got: {value}")


def require_non_negative(label: str, value: float) -> None:
    if value < 0:
        raise SystemExit(f"{label} must be 0 or greater. Got: {value}")


def validate_model_name(model: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", model):
        raise SystemExit("model must start with a letter/number/_ and contain only letters, numbers, _, ., or -")


def validate_color(color: list[float]) -> None:
    if len(color) != 4:
        raise SystemExit("--color must have four values: R G B A")
    if any(value < 0.0 or value > 1.0 for value in color):
        raise SystemExit("--color values must be between 0.0 and 1.0")


def generated_sdf_path(model: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", model)
    return GENERATED_MODEL_DIR / f"{safe_name}.sdf"


def build_box_sdf(
    *,
    model: str,
    size_x: float,
    size_y: float,
    size_z: float,
    mass: float,
    color: list[float],
    is_static: bool,
    write_file: bool,
) -> Path:
    require_positive("size_x", size_x)
    require_positive("size_y", size_y)
    require_positive("size_z", size_z)
    require_positive("mass", mass)
    validate_model_name(model)
    validate_color(color)

    ixx = mass * (size_y**2 + size_z**2) / 12.0
    iyy = mass * (size_x**2 + size_z**2) / 12.0
    izz = mass * (size_x**2 + size_y**2) / 12.0
    color_text = " ".join(f"{value:.3f}" for value in color)
    size_text = f"{size_x:.3f} {size_y:.3f} {size_z:.3f}"
    link_z = size_z / 2.0
    sdf_path = generated_sdf_path(model)

    if write_file:
        GENERATED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
        sdf_path.write_text(
            f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{escape(model)}">
    <static>{str(is_static).lower()}</static>
    <link name="link">
      <pose>0 0 {link_z:.3f} 0 0 0</pose>
      <collision name="collision">
        <geometry>
          <box><size>{size_text}</size></box>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <box><size>{size_text}</size></box>
        </geometry>
        <material>
          <ambient>{color_text}</ambient>
          <diffuse>{color_text}</diffuse>
        </material>
      </visual>
      <inertial>
        <mass>{mass:.3f}</mass>
        <inertia>
          <ixx>{ixx:.6f}</ixx><iyy>{iyy:.6f}</iyy><izz>{izz:.6f}</izz>
          <ixy>0</ixy><ixz>0</ixz><iyz>0</iyz>
        </inertia>
      </inertial>
    </link>
  </model>
</sdf>
""",
            encoding="utf-8",
        )
    return sdf_path


def resolve_sdf(
    *,
    sdf: str | None,
    model: str,
    size_x: float,
    size_y: float,
    size_z: float,
    mass: float,
    color: list[float],
    is_static: bool,
    dry_run: bool,
) -> Path | None:
    if sdf:
        sdf_path = Path(sdf)
        if not sdf_path.is_absolute():
            sdf_path = ROOT / sdf_path
        if not sdf_path.exists():
            print_status(False, "custom sdf", str(sdf_path))
            return None
        return sdf_path.resolve()

    return build_box_sdf(
        model=model,
        size_x=size_x,
        size_y=size_y,
        size_z=size_z,
        mass=mass,
        color=color,
        is_static=is_static,
        write_file=True,
    )


def wait_after(label: str, seconds: float, dry_run: bool) -> None:
    require_non_negative(label, seconds)
    if seconds == 0:
        return
    if dry_run:
        print(f"[DRY-RUN] wait {seconds}s after {label}")
        return
    print(f"Waiting {seconds}s after {label}...")
    time.sleep(seconds)


def service_names() -> set[str]:
    result = ros2(["service", "list"], timeout=5.0)
    if result.returncode != 0:
        print(result.stderr.strip())
        return set()
    return set(line.strip() for line in result.stdout.splitlines() if line.strip())


def spawn_box(
    *,
    x: float,
    y: float,
    z: float,
    model: str,
    size_x: float,
    size_y: float,
    size_z: float,
    mass: float,
    color: list[float],
    is_static: bool,
    sdf: str | None,
    spawn_timeout: float,
    wait_after_spawn: float,
    dry_run: bool,
) -> int:
    require_positive("spawn_timeout", spawn_timeout)
    sdf_path = resolve_sdf(
        sdf=sdf,
        model=model,
        size_x=size_x,
        size_y=size_y,
        size_z=size_z,
        mass=mass,
        color=color,
        is_static=is_static,
        dry_run=dry_run,
    )
    if sdf_path is None:
        return 1
    if not sdf:
        print(
            "Box parameters: "
            f"size=({size_x}, {size_y}, {size_z}) "
            f"mass={mass} static={is_static} color={color} sdf={sdf_path}"
        )
    code = run_stream(
        [
            "timeout",
            str(spawn_timeout),
            "gz",
            "model",
            "--spawn-file",
            str(sdf_path),
            "--model-name",
            model,
            "--pose-x",
            str(x),
            "--pose-y",
            str(y),
            "--pose-z",
            str(z),
        ],
        dry_run=dry_run,
    )
    if code == 0:
        wait_after("spawn", wait_after_spawn, dry_run)
    return code


def clear_costmaps(clear_timeout: float, wait_after_clear: float, dry_run: bool) -> int:
    require_positive("clear_timeout", clear_timeout)
    if dry_run:
        for service in CLEAR_SERVICES:
            run_stream(
                ["timeout", str(clear_timeout), "ros2", "service", "call", service, "nav2_msgs/srv/ClearEntireCostmap", "{request: {}}"],
                dry_run=True,
            )
        wait_after("clear", wait_after_clear, dry_run)
        return 0

    services = service_names()
    failures = 0
    for service in CLEAR_SERVICES:
        if service not in services:
            print_status(False, f"service {service}")
            failures += 1
            continue
        code = run_stream(
            ["timeout", str(clear_timeout), "ros2", "service", "call", service, "nav2_msgs/srv/ClearEntireCostmap", "{request: {}}"],
            dry_run=dry_run,
        )
        failures += 0 if code == 0 else 1
    if failures == 0:
        wait_after("clear", wait_after_clear, dry_run)
    return 0 if failures == 0 else 1


def delete_box(model: str, delete_timeout: float, dry_run: bool) -> int:
    require_positive("delete_timeout", delete_timeout)
    validate_model_name(model)
    if dry_run:
        return run_stream(
            ["timeout", str(delete_timeout), "gz", "model", "--model-name", model, "--delete"],
            dry_run=True,
        )

    return run_stream(["timeout", str(delete_timeout), "gz", "model", "--model-name", model, "--delete"], dry_run=dry_run)


def spawn_command(args: argparse.Namespace) -> list[str]:
    command = [
        "python3",
        "scripts/lab6_practice.py",
        "--action",
        "spawn",
        "--x",
        str(args.x),
        "--y",
        str(args.y),
        "--z",
        str(args.z),
        "--model",
        args.model,
        "--size-x",
        str(args.size_x),
        "--size-y",
        str(args.size_y),
        "--size-z",
        str(args.size_z),
        "--mass",
        str(args.mass),
        "--color",
        *[str(value) for value in args.color],
        "--spawn-timeout",
        str(args.spawn_timeout),
    ]
    if args.static:
        command.append("--static")
    if args.sdf:
        command.extend(["--sdf", args.sdf])
    if args.wait_after_spawn:
        command.extend(["--wait-after-spawn", str(args.wait_after_spawn)])
    return command


def print_commands(args: argparse.Namespace) -> None:
    commands = [
        ["source", "scripts/env.sh"],
        spawn_command(args),
        [
            "python3",
            "scripts/lab6_practice.py",
            "--action",
            "clear",
            "--clear-timeout",
            str(args.clear_timeout),
        ],
        [
            "python3",
            "scripts/lab6_practice.py",
            "--action",
            "delete",
            "--model",
            args.model,
            "--delete-timeout",
            str(args.delete_timeout),
        ],
    ]
    for command in commands:
        print(quote_command(command))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=["commands", "spawn", "clear", "delete", "cycle"], default="commands")
    parser.add_argument("--x", type=float, default=0.5)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=0.25)
    parser.add_argument("--model", default="lab_box")
    parser.add_argument("--size-x", type=float, default=0.35)
    parser.add_argument("--size-y", type=float, default=0.35)
    parser.add_argument("--size-z", type=float, default=0.5)
    parser.add_argument("--mass", type=float, default=1.0)
    parser.add_argument("--color", nargs=4, type=float, default=[0.8, 0.1, 0.1, 1.0], metavar=("R", "G", "B", "A"))
    parser.add_argument("--sdf", default=None, help="Use a custom SDF file instead of generating a box model.")
    parser.add_argument("--static", action="store_true", help="Spawn the obstacle as a static Gazebo model.")
    parser.add_argument("--spawn-timeout", type=float, default=10.0)
    parser.add_argument("--clear-timeout", type=float, default=10.0)
    parser.add_argument("--delete-timeout", type=float, default=10.0)
    parser.add_argument("--wait-after-spawn", type=float, default=0.0)
    parser.add_argument("--wait-after-clear", type=float, default=0.0)
    parser.add_argument("--keep-after-cycle", action="store_true", help="For cycle action, do not delete the obstacle at the end.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.action == "commands":
        print_commands(args)
    elif args.action == "spawn":
        raise SystemExit(
            spawn_box(
                x=args.x,
                y=args.y,
                z=args.z,
                model=args.model,
                size_x=args.size_x,
                size_y=args.size_y,
                size_z=args.size_z,
                mass=args.mass,
                color=args.color,
                is_static=args.static,
                sdf=args.sdf,
                spawn_timeout=args.spawn_timeout,
                wait_after_spawn=args.wait_after_spawn,
                dry_run=args.dry_run,
            )
        )
    elif args.action == "clear":
        raise SystemExit(clear_costmaps(args.clear_timeout, args.wait_after_clear, args.dry_run))
    elif args.action == "delete":
        raise SystemExit(delete_box(args.model, args.delete_timeout, args.dry_run))
    elif args.action == "cycle":
        code = spawn_box(
            x=args.x,
            y=args.y,
            z=args.z,
            model=args.model,
            size_x=args.size_x,
            size_y=args.size_y,
            size_z=args.size_z,
            mass=args.mass,
            color=args.color,
            is_static=args.static,
            sdf=args.sdf,
            spawn_timeout=args.spawn_timeout,
            wait_after_spawn=args.wait_after_spawn,
            dry_run=args.dry_run,
        )
        if code == 0:
            code = clear_costmaps(args.clear_timeout, args.wait_after_clear, args.dry_run)
        if code == 0 and not args.keep_after_cycle:
            code = delete_box(args.model, args.delete_timeout, args.dry_run)
        elif code == 0:
            print(f"Keeping obstacle model={args.model}. Delete later with --action delete --model {args.model}")
        raise SystemExit(code)


if __name__ == "__main__":
    main()
