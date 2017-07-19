from defuzz import Defuzzer


def test_it():
    dfz = Defuzzer()
    assert dfz.defuzz((1, 2)) == (1, 2)
    assert dfz.defuzz((1, 3)) == (1, 3)
    assert dfz.defuzz((1.00000001, 2)) == (1, 2)
    assert dfz.defuzz((1, 2, 3, 4, 5)) == (1, 2, 3, 4, 5)
    assert dfz.defuzz((2.00000001, 3)) == (2.00000001, 3)
    assert dfz.defuzz((2, 3)) == (2.00000001, 3)
