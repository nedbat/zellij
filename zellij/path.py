"""A zigzag path, a sequence of points."""

import collections

from .defuzz import Defuzzer
from .euclid import collinear, Point, Line, Segment, Bounds
from .postulates import adjacent_pairs, triples


class Path:
    def __init__(self, points):
        self.points = tuple(points)

    def __repr__(self):
        return f"<Path {list(self.points)}>"

    def __eq__(self, other):
        return self.points == other.points

    def __hash__(self):
        return hash(self.points)

    def __lt__(self, other):
        return self.points < other.points

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def __getitem__(self, idx):
        # Lots of code tries to get the endpoints by index. Allow that but
        # nothing else.
        assert idx in [0, -1]
        return self.points[idx]

    @property
    def closed(self):
        """Does the path loop? Start and end are the same points."""
        return self.points[0] == self.points[-1]

    def length(self):
        """The euclidean distance along the path."""
        return sum(p1.distance(p2) for p1, p2 in adjacent_pairs(self.points))

    def ends(self):
        yield self.points[0]
        yield self.points[-1]

    def bounds(self):
        """What is the `Bounds` for this path?"""
        return Bounds.points(self.points)

    def segments(self):
        for p1, p2 in adjacent_pairs(self.points):
            yield Segment(tuple(p1), tuple(p2))

    def any_collinear(self):
        """Are any of the parts of this path collinear?"""
        return any(collinear(*them) for them in triples(self.points))

    def clean(self):
        """Remove unneeded points from a path."""
        if len(self.points) <= 2:
            return self

        # Points are unneeded if they are collinear with their neighbors.
        new_points = []
        if not self.closed:
            new_points.append(self.points[0])

        for a, b, c in triples(self.points):
            if not collinear(a, b, c):
                new_points.append(b)

        if self.closed:
            new_points.append(new_points[0])
        else:
            new_points.append(self.points[-1])

        return Path(new_points)

    def reversed(self):
        return Path(self.points[::-1])

    def draw(self, ctx, append=False, reverse=False):
        points = self.points
        if reverse:
            points = points[::-1]

        (ctx.line_to if append else ctx.move_to)(*points[0])

        for pt in points[1:-1]:
            ctx.line_to(*pt)

        if self.closed:
            ctx.close_path()
        else:
            ctx.line_to(*points[-1])

    def offset_path(self, offset):
        lines = []
        for p1, p2 in adjacent_pairs(self.points):
            lines.append(Line(p1, p2).offset(offset))

        points = []
        if self.closed:
            p0 = lines[-1].intersect(lines[0])
            points.append(p0)
        else:
            points.append(lines[0].p1)

        for l1, l2 in adjacent_pairs(lines):
            points.append(l1.intersect(l2))

        if self.closed:
            points.append(p0)
        else:
            points.append(lines[-1].p2)

        return Path(points)

    def defuzz(self, defuzz):
        return Path([Point(*defuzz(pt)) for pt in self.points])

    def penultimate(self, point):
        """The second-to-last point from whichever end ends with `point`."""
        if self.points[0] == point:
            return self.points[1]
        else:
            assert self.points[-1] == point
            return self.points[-2]

    def join(self, p2):
        """Join `self` and `p2` together by their common endpoint."""
        p1 = self.points
        p2 = p2.points

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

        return Path(p1 + p2)

    def trim(self, end, trimmers):
        """Trim one end of path where trimmers (paths) cross it."""
        points = list(self.points)
        seg = Segment(*points[[None, -2][end]:[2, None][end]])
        cuts = [pt for t in trimmers for pt in seg_path_intersections(seg, t)]
        if cuts:
            cuts = seg.sort_along(cuts)
            if end == 0:
                points = [cuts[-1]] + points[1:]
            else:
                points = points[:-1] + [cuts[0]]
            return Path(points)
        else:
            return self

    def canonicalize(self):
        """Produce an equivalent canonical path."""
        if self.closed:
            points = list(self.points[:-1])
            points = min((points[i:]+points[:i])[::s] for i in range(len(points)) for s in [1, -1])
            points.append(points[0])
            return Path(points)
        else:
            return Path(min(self.points, self.points[::-1]))


def defuzz_paths(paths):
    defuzz = Defuzzer().defuzz
    return [path.defuzz(defuzz) for path in paths]

def combine_paths(paths):
    paths = defuzz_paths(paths)
    pm = collections.defaultdict(list)
    for path in paths:
        for end in path.ends():
            pm[end].append(path)

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
                    path = path.join(other)
                    pm[path[0]].append(path)
                    pm[path[-1]].append(path)
                else:
                    break

        used.add(id(path))
        combined.append(path.clean())

    return combined

def draw_paths(paths, ctx):
    for path in paths:
        path.draw(ctx)


def best_join(path, join_point, possibilities):
    others = [p for p in possibilities if p != path]

    # If there's only one other path, then join to that one.
    if len(others) == 1:
        return others[0]

    # If there's more than one, find one we are collinear with.
    path_pen = path.penultimate(join_point)
    for other in others:
        other_pen = other.penultimate(join_point)
        if collinear(path_pen, join_point, other_pen):
            return other

    return None

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

def paths_bounds(paths):
    """Return the `Bounds` of the paths."""
    bounds = paths[0].bounds()
    for path in paths:
        bounds |= path.bounds()
    return bounds

def clip_paths(paths, bounds):
    """Return the paths that overlap the bounds."""
    return [path for path in paths if path.bounds().overlap(bounds)]

def equal_path(path1, path2):
    return path1.canonicalize() == path2.canonicalize()

def canonicalize_paths(paths):
    """Canonicalize a list of paths."""
    paths = [p.canonicalize() for p in paths]
    paths.sort()
    return paths

def equal_paths(paths1, paths2):
    """Are the paths in paths1 and paths2 equivalent?"""
    return canonicalize_paths(paths1) == canonicalize_paths(paths2)

def paths_length(paths):
    return sum(path.length() for path in paths)

def seg_path_intersections(segment, path):
    """Return a list of all the points where segment and path intersect."""
    for pseg in path.segments():
        pt = segment.intersect(pseg)
        if pt is not None:
            yield pt
