from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from map_utils import load_map, world_to_grid, grid_to_world, shortest_path, path_length_world, plan_path


def test_load_example_map():
    g = load_map(Path(__file__).resolve().parents[1] / 'examples' / 'simple_map.yaml')
    assert g.width > 0 and g.height > 0
    assert g.resolution > 0


def test_world_grid_roundtrip():
    g = load_map(Path(__file__).resolve().parents[1] / 'examples' / 'simple_map.yaml')
    r, c = world_to_grid(g, 0.0, 0.0)
    x, y = grid_to_world(g, r, c)
    assert abs(x) < 0.1 and abs(y) < 0.1


def test_dijkstra_and_astar_path():
    g = load_map(Path(__file__).resolve().parents[1] / 'examples' / 'simple_map.yaml')
    s = world_to_grid(g, -1.5, -1.5)
    q = world_to_grid(g, 1.5, 1.5)
    for alg in ['dijkstra', 'astar']:
        path, expanded = shortest_path(g, s, q, alg)
        assert len(path) > 2
        assert expanded > 0
        assert path_length_world(g, path) > 0


def test_extra_planners_path():
    g = load_map(Path(__file__).resolve().parents[1] / 'examples' / 'simple_map.yaml')
    s = world_to_grid(g, 0.0, 0.0)
    q = world_to_grid(g, 1.0, 1.0)
    for alg in ['greedy', 'weighted_astar', 'rrt']:
        path, expanded = plan_path(g, s, q, alg, rrt_seed=4)
        assert len(path) > 1
        assert expanded > 0
        assert path_length_world(g, path) > 0
