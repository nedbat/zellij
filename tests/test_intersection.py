from hypothesis import assume, given
from hypothesis.strategies import builds, lists, integers, tuples

from zellij.defuzz import Defuzzer
from zellij.euclid import collinear, Segment, BadGeometry
from zellij.intersection import segment_intersections
from zellij.postulates import all_pairs


nums = integers(min_value=-1000, max_value=1000)
points = tuples(nums, nums)
segments = builds(lambda l: Segment(*l), lists(points, min_size=2, max_size=2, unique=True))

@given(lists(segments, min_size=2, max_size=100, unique=True))
def test_intersections(segments):
    defuzz = Defuzzer().defuzz

    # Check that none of our segment pairs are pathological, and collect the
    # true answers the hard way, by checking pair-wise.
    true = set()
    for s1, s2 in all_pairs(segments):
        try:
            ipt = s1.intersect(s2)
            if ipt is not None:
                true.add(defuzz(ipt))
        except BadGeometry:
            # If two segments don't have an answer, then don't use this test
            # case.
            assume(False)

    # Run the actual function we care about.
    isects = segment_intersections(segments)

    for pt, segs in isects.items():
        # Property: the answer should be in the true answers we found the hard
        # way.
        assert defuzz(pt) in true

        # Property: every intersection should be collinear with the segment it
        # claims to be part of.
        for seg in segs:
            s1, s2 = seg
            assert collinear(s1, pt, s2)
