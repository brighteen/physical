#!/usr/bin/env python3
"""Map utilities for ND3-15 offline planner labs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import heapq
from typing import Dict, Iterable, List, Tuple

import numpy as np
import yaml
from PIL import Image


GRID_PLANNERS = ("dijkstra", "astar", "greedy", "weighted_astar")
SAMPLING_PLANNERS = ("rrt",)
SUPPORTED_PLANNERS = GRID_PLANNERS + SAMPLING_PLANNERS


@dataclass
class GridMap:
    yaml_path: Path
    image_path: Path
    resolution: float
    origin: Tuple[float, float, float]
    image: np.ndarray  # grayscale 0..255, shape HxW
    free_mask: np.ndarray  # True where free

    @property
    def height(self) -> int:
        return int(self.image.shape[0])

    @property
    def width(self) -> int:
        return int(self.image.shape[1])


def load_map(yaml_path: str | Path) -> GridMap:
    yp = Path(yaml_path).expanduser().resolve()
    if not yp.exists():
        raise FileNotFoundError(f"Map YAML not found: {yp}")
    with yp.open("r", encoding="utf-8") as f:
        meta = yaml.safe_load(f) or {}
    img_ref = meta.get("image")
    if not img_ref:
        raise ValueError(f"Map YAML has no image field: {yp}")
    ip = (yp.parent / img_ref).resolve()
    if not ip.exists():
        raise FileNotFoundError(f"Map image not found: {ip}")
    img = np.asarray(Image.open(ip).convert("L"))
    resolution = float(meta.get("resolution", 0.05))
    origin_raw = meta.get("origin", [0.0, 0.0, 0.0])
    origin = (float(origin_raw[0]), float(origin_raw[1]), float(origin_raw[2]))
    # ROS map convention: high value is free in typical PGM, low value is occupied.
    # Treat unknown 205 as not free for conservative planning.
    free_thresh = float(meta.get("free_thresh", 0.25))
    # occupancy probability = (255 - pixel) / 255
    occ_prob = (255.0 - img.astype(float)) / 255.0
    free_mask = occ_prob < free_thresh
    return GridMap(yp, ip, resolution, origin, img, free_mask)


def world_to_grid(gmap: GridMap, x: float, y: float) -> Tuple[int, int]:
    gx = int(math.floor((x - gmap.origin[0]) / gmap.resolution))
    gy_from_bottom = int(math.floor((y - gmap.origin[1]) / gmap.resolution))
    row = gmap.height - 1 - gy_from_bottom
    col = gx
    return row, col


def grid_to_world(gmap: GridMap, row: int, col: int) -> Tuple[float, float]:
    x = gmap.origin[0] + (col + 0.5) * gmap.resolution
    gy_from_bottom = gmap.height - 1 - row
    y = gmap.origin[1] + (gy_from_bottom + 0.5) * gmap.resolution
    return x, y


def in_bounds(gmap: GridMap, cell: Tuple[int, int]) -> bool:
    r, c = cell
    return 0 <= r < gmap.height and 0 <= c < gmap.width


def is_free(gmap: GridMap, cell: Tuple[int, int]) -> bool:
    return in_bounds(gmap, cell) and bool(gmap.free_mask[cell])


def nearest_free(gmap: GridMap, cell: Tuple[int, int], max_radius: int = 60) -> Tuple[int, int]:
    if is_free(gmap, cell):
        return cell
    r0, c0 = cell
    for rad in range(1, max_radius + 1):
        for dr in range(-rad, rad + 1):
            for dc in (-rad, rad):
                cand = (r0 + dr, c0 + dc)
                if is_free(gmap, cand):
                    return cand
        for dc in range(-rad + 1, rad):
            for dr in (-rad, rad):
                cand = (r0 + dr, c0 + dc)
                if is_free(gmap, cand):
                    return cand
    raise ValueError(f"No free cell found near {cell}")


def neighbors8(gmap: GridMap, cell: Tuple[int, int]) -> Iterable[Tuple[Tuple[int, int], float]]:
    r, c = cell
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nb = (r + dr, c + dc)
            if is_free(gmap, nb):
                yield nb, math.sqrt(2.0) if dr and dc else 1.0


def reconstruct(parent: Dict[Tuple[int, int], Tuple[int, int]], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    path = [goal]
    while path[-1] in parent:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def shortest_path(
    gmap: GridMap,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    algorithm: str = "astar",
    heuristic_weight: float = 1.5,
) -> Tuple[List[Tuple[int, int]], int]:
    if algorithm not in GRID_PLANNERS:
        raise ValueError(f"Unsupported grid planner: {algorithm}. Choose one of {GRID_PLANNERS}")
    start = nearest_free(gmap, start)
    goal = nearest_free(gmap, goal)

    def h(cell: Tuple[int, int]) -> float:
        return math.hypot(goal[0] - cell[0], goal[1] - cell[1])

    def priority(g_cost: float, cell: Tuple[int, int]) -> float:
        if algorithm == "dijkstra":
            return g_cost
        if algorithm == "greedy":
            return h(cell)
        if algorithm == "weighted_astar":
            return g_cost + heuristic_weight * h(cell)
        return g_cost + h(cell)

    pq: List[Tuple[float, float, Tuple[int, int]]] = []
    heapq.heappush(pq, (0.0, 0.0, start))
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
    gscore: Dict[Tuple[int, int], float] = {start: 0.0}
    expanded = 0
    visited = set()

    while pq:
        _, gcur, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        expanded += 1
        if cur == goal:
            return reconstruct(parent, cur), expanded
        for nb, step in neighbors8(gmap, cur):
            ng = gcur + step
            if ng < gscore.get(nb, float("inf")):
                gscore[nb] = ng
                parent[nb] = cur
                f = priority(ng, nb)
                heapq.heappush(pq, (f, ng, nb))
    raise RuntimeError("No path found")


def line_cells(start: Tuple[int, int], goal: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
    r0, c0 = start
    r1, c1 = goal
    steps = max(abs(r1 - r0), abs(c1 - c0))
    if steps == 0:
        yield start
        return
    for i in range(steps + 1):
        t = i / steps
        yield int(round(r0 + (r1 - r0) * t)), int(round(c0 + (c1 - c0) * t))


def line_is_free(gmap: GridMap, start: Tuple[int, int], goal: Tuple[int, int]) -> bool:
    return all(is_free(gmap, cell) for cell in line_cells(start, goal))


def densify_path(path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not path:
        return []
    dense: List[Tuple[int, int]] = []
    for i in range(len(path) - 1):
        segment = list(line_cells(path[i], path[i + 1]))
        if dense:
            segment = segment[1:]
        dense.extend(segment)
    return dense or path[:]


def _sample_free_cell(gmap: GridMap, rng: np.random.Generator) -> Tuple[int, int]:
    rows, cols = np.nonzero(gmap.free_mask)
    if len(rows) == 0:
        raise RuntimeError("Map has no free cells")
    idx = int(rng.integers(0, len(rows)))
    return int(rows[idx]), int(cols[idx])


def _nearest_vertex(vertices: List[Tuple[int, int]], target: Tuple[int, int]) -> Tuple[int, int]:
    return min(vertices, key=lambda cell: math.hypot(target[0] - cell[0], target[1] - cell[1]))


def _steer(from_cell: Tuple[int, int], to_cell: Tuple[int, int], step_cells: int) -> Tuple[int, int]:
    dr = to_cell[0] - from_cell[0]
    dc = to_cell[1] - from_cell[1]
    dist = math.hypot(dr, dc)
    if dist <= step_cells:
        return to_cell
    scale = step_cells / dist
    return int(round(from_cell[0] + dr * scale)), int(round(from_cell[1] + dc * scale))


def rrt_path(
    gmap: GridMap,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    iterations: int = 4000,
    step_cells: int = 10,
    goal_sample_rate: float = 0.15,
    goal_radius_cells: int = 10,
    seed: int = 7,
) -> Tuple[List[Tuple[int, int]], int]:
    if iterations < 1:
        raise ValueError("RRT iterations must be at least 1")
    if step_cells < 1:
        raise ValueError("RRT step_cells must be at least 1")
    if not 0.0 <= goal_sample_rate <= 1.0:
        raise ValueError("RRT goal_sample_rate must be between 0 and 1")

    start = nearest_free(gmap, start)
    goal = nearest_free(gmap, goal)
    rng = np.random.default_rng(seed)

    vertices = [start]
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

    for _ in range(iterations):
        sample = goal if rng.random() < goal_sample_rate else _sample_free_cell(gmap, rng)
        nearest = _nearest_vertex(vertices, sample)
        new_cell = _steer(nearest, sample, step_cells)
        if new_cell == nearest or not is_free(gmap, new_cell):
            continue
        if not line_is_free(gmap, nearest, new_cell):
            continue
        if new_cell in parent:
            continue

        parent[new_cell] = nearest
        vertices.append(new_cell)

        near_goal = math.hypot(goal[0] - new_cell[0], goal[1] - new_cell[1]) <= goal_radius_cells
        if near_goal and line_is_free(gmap, new_cell, goal):
            parent[goal] = new_cell
            return reconstruct(parent, goal), len(vertices)

    raise RuntimeError(f"RRT failed to find a path after {iterations} iterations")


def plan_path(
    gmap: GridMap,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    algorithm: str = "astar",
    heuristic_weight: float = 1.5,
    rrt_iterations: int = 4000,
    rrt_step_cells: int = 10,
    rrt_goal_sample_rate: float = 0.15,
    rrt_goal_radius_cells: int = 10,
    rrt_seed: int = 7,
) -> Tuple[List[Tuple[int, int]], int]:
    if algorithm in GRID_PLANNERS:
        return shortest_path(gmap, start, goal, algorithm, heuristic_weight=heuristic_weight)
    if algorithm == "rrt":
        return rrt_path(
            gmap,
            start,
            goal,
            iterations=rrt_iterations,
            step_cells=rrt_step_cells,
            goal_sample_rate=rrt_goal_sample_rate,
            goal_radius_cells=rrt_goal_radius_cells,
            seed=rrt_seed,
        )
    raise ValueError(f"Unsupported planner: {algorithm}. Choose one of {SUPPORTED_PLANNERS}")


def path_length_world(gmap: GridMap, path: List[Tuple[int, int]]) -> float:
    if len(path) < 2:
        return 0.0
    pts = [grid_to_world(gmap, *p) for p in path]
    return sum(math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1))
