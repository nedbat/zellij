"""A zigzag path, a sequence of points."""

import collections

from .defuzz import Defuzzer
from .euclid import collinear, Point, Line, Segment
from .postulates import adjacent_pairs

def defuzz_paths(paths):
    dfz = Defuzzer()
    dfpaths = []
    for path in paths:
        dfpath = []
        for pt in path:
            dfpath.append(Point(*dfz.defuzz(pt)))
        dfpaths.append(dfpath)
    return dfpaths

def combine_paths(paths):
    paths = defuzz_paths(paths)
    pm = collections.defaultdict(list)
    for path in paths:
        pm[path[0]].append(path)
        pm[path[-1]].append(path)

    combined = []
    used = set()

    for path in paths:
        if id(path) in used:
            continue
        for end in [0, -1]:
            while True:
                target = path[end]
                possibilities = pm[target]
                possibilities = [p for p in possibilities if id(p) not in used]
                if not possibilities:
                    break
                other = best_join(path, target, possibilities)
                if other is not None:
                    used.add(id(path))
                    used.add(id(other))
                    path = join_paths(path, other)
                    pm[path[0]].append(path)
                    pm[path[-1]].append(path)
                else:
                    break

        used.add(id(path))
        combined.append(clean_path(path))

    return combined

def replay_path(path, ctx, append=False):
    (ctx.line_to if append else ctx.move_to)(*path[0])

    for pt in path[1:-1]:
        ctx.line_to(*pt)

    if path[-1] == path[0]:
        ctx.close_path()
    else:
        ctx.line_to(*path[-1])


def replay_paths(paths, ctx):
    for path in paths:
        replay_path(path, ctx)


def path_in_box(path, ll, ur):
    return all(pt.in_box(ll, ur) for pt in path)


def penultimate(path, point):
    """The second-to-last point from whichever end ends with `point`."""
    if path[0] == point:
        return path[1]
    else:
        assert path[-1] == point
        return path[-2]

def best_join(path, join_point, possibilities):
    others = [p for p in possibilities if p != path]

    # If there's only one other path, then join to that one.
    if len(others) == 1:
        return others[0]

    # If there's more than one, find one we are collinear with.
    path_pen = penultimate(path, join_point)
    for other in others:
        other_pen = penultimate(other, join_point)
        if collinear(path_pen, join_point, other_pen):
            return other

    return None

def join_paths(p1, p2):
    """Join `p1` and `p2` together by their common endpoint."""
    # Find the ends that are the same point. Rearrange p1 and p2 so that p1+p2
    # is the join we need, and remove the duplicate point at p2[0].
    if p1[-1] == p2[0]:
        p2 = p2[1:]
    elif p1[-1] == p2[-1]:
        p2 = p2[-2::-1]
    elif p1[0] == p2[-1]:
        p1, p2 = p2, p1[1:]
    elif p1[0] == p2[0]:
        p1, p2 = p1[::-1], p2[1:]
    else:
        return None

    # If the join would have a redundant point because of three collinear
    # points in a row, then remove the middle point.
    if collinear(p1[-2], p1[-1], p2[0]):
        p1 = p1[:-1]

    return p1 + p2

def show_path(path):
    if path is None:
        return "None"
    return f"Path[{path[0]}..{len(path)}..{path[-1]}]@{id(path)}"

def show_paths(paths):
    ret = "[\n"
    for path in paths:
        ret += f"    {show_path(path)}\n"
    ret += "]"
    return ret

def triple_points(path):
    """Iterate over the triples of consecutive points along the path."""
    # Take care to include the triples across the ends if the path is a loop.
    if path[0] == path[-1]:
        path = path + path[1:2]
    return zip(path, path[1:], path[2:])

def clean_path(path):
    """Remove unneeded points from a path."""
    if len(path) <= 2:
        return path

    # Points are unneeded if they are collinear with their neighbors.
    closed = (path[0] == path[-1])
    new_path = []
    if not closed:
        new_path.append(path[0])

    for a, b, c in triple_points(path):
        if not collinear(a, b, c):
            new_path.append(b)

    if closed:
        new_path.append(new_path[0])
    else:
        new_path.append(path[-1])

    return new_path


def offset_path(path, offset):
    closed = (path[0] == path[-1])

    lines = []
    for p1, p2 in adjacent_pairs(path):
        lines.append(Line(p1, p2).offset(offset))

    points = []
    if closed:
        p0 = lines[-1].intersect(lines[0])
        points.append(p0)
    else:
        points.append(lines[0].p1)

    for l1, l2 in adjacent_pairs(lines):
        points.append(l1.intersect(l2))

    if closed:
        points.append(p0)
    else:
        points.append(lines[-1].p2)

    return points

def paths_box(paths):
    """Return the (ll, ur) pair of points that define the bounding box."""
    minx = min(p.x for path in paths for p in path)
    maxx = max(p.x for path in paths for p in path)
    miny = min(p.y for path in paths for p in path)
    maxy = max(p.y for path in paths for p in path)
    return Point(minx, miny), Point(maxx, maxy)


def canonicalize_path(path):
    """Produce an equivalent canonical path."""
    if path[0] == path[-1]:
        path = path[:-1]
        path = min((path[i:]+path[:i])[::s] for i in range(len(path)) for s in [1, -1])
        path.append(path[0])
        return path
    else:
        return min(path, path[::-1])

def equal_path(path1, path2):
    return canonicalize_path(path1) == canonicalize_path(path2)

def canonicalize_paths(paths):
    """Canonicalize a list of paths."""
    paths = [canonicalize_path(p) for p in paths]
    paths.sort()
    return paths

def equal_paths(paths1, paths2):
    """Are the paths in paths1 and paths2 equivalent?"""
    return canonicalize_paths(paths1) == canonicalize_paths(paths2)

def path_length(path):
    return sum(p1.distance(p2) for p1, p2 in adjacent_pairs(path))

def paths_length(paths):
    return sum(path_length(path) for path in paths)

def path_segments(path):
    for p1, p2 in adjacent_pairs(path):
        yield Segment(tuple(p1), tuple(p2))

def seg_path_intersections(segment, path):
    """Return a list of all the points where segment and path intersect."""
    for pseg in path_segments(path):
        pt = segment.intersect(pseg)
        if pt is not None:
            yield pt

def trim_path(path, end, trimmers):
    """Trim one end of path where trimmers (paths) cross it."""
    seg = Segment(*path[[None, -2][end]:[2, None][end]])
    cuts = [pt for t in trimmers for pt in seg_path_intersections(seg, t)]
    if cuts:
        cuts = seg.sort_along(cuts)
        if end == 0:
            path = [cuts[-1]] + path[1:]
        else:
            path = path[:-1] + [cuts[0]]
    return path
