from geopip._geo_fkt import in_bbox


def test_in_bbox():
    assert in_bbox((0.5, 0.5), (0, 0, 1, 1))  # middle
    assert in_bbox((0, 0.5), (0, 0, 1, 1))  # on left edge
    assert in_bbox((0.5, 0), (0, 0, 1, 1))  # on bottom edge
    assert in_bbox((1, 0.5), (0, 0, 1, 1))  # on right edge
    assert in_bbox((0.5, 1), (0, 0, 1, 1))  # on top edge

    assert not in_bbox((0.5, 2), (0, 0, 1, 1))  # above
    assert not in_bbox((0.5, -1), (0, 0, 1, 1))  # below
    assert not in_bbox((-1, 0.5), (0, 0, 1, 1))  # left
    assert not in_bbox((2, 0.5), (0, 0, 1, 1))  # right

    assert not in_bbox((-0.5, -0.5), (0, 0, 1, 1))  # left bottom
    assert not in_bbox((1.5, -0.5), (0, 0, 1, 1))  # right bottom
    assert not in_bbox((-0.5, 1.5), (0, 0, 1, 1))  # left top
    assert not in_bbox((1.5, 1.5), (0, 0, 1, 1))  # right top
