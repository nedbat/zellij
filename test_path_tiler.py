from path_tiler import PathTiler

def extern_path(pt):
    return [path.ops for path in pt.paths]


def test_do_nothing():
    pt = PathTiler()
    assert pt.paths == []


def test_two_segments():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.line_to(150, 200)
    pt.move_to(17, 17)
    pt.rel_line_to(100, 200)
    pt.close_path()
    assert extern_path(pt) == [
        [('move_to', 100.0, 100.0), ('line_to', 150.0, 200.0)],
        [('move_to', 17.0, 17.0), ('line_to', 117.0, 217.0), ('close_path',)],
    ]


def test_translation():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.translate(1000, 2000)
    pt.line_to(10, 20)
    assert extern_path(pt) == [
        [('move_to', 100.0, 100.0), ('line_to', 1010.0, 2020.0)],
    ]


def test_save_restore():
    pt = PathTiler()
    pt.move_to(100, 100)
    pt.translate(1000, 2000)
    pt.line_to(10, 20)
    pt.save()
    pt.translate(1, 2)
    pt.move_to(1, 2)
    pt.line_to(2, 4)
    pt.restore()
    pt.move_to(1, 2)
    pt.line_to(2, 4)
    assert extern_path(pt) == [
        [('move_to', 100.0, 100.0), ('line_to', 1010.0, 2020.0)],
        [('move_to', 1002.0, 2004.0), ('line_to', 1003.0, 2006.0)],
        [('move_to', 1001.0, 2002.0), ('line_to', 1002.0, 2004.0)],
    ]


def test_rel_line_to():
    pt = PathTiler()
    pt.translate(1000, 2000)
    pt.move_to(0, 0)
    pt.rel_line_to(100, 200)
    assert extern_path(pt) == [
        [('move_to', 1000.0, 2000.0), ('line_to', 1100.0, 2200.0)],
    ]
