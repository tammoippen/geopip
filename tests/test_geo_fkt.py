# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from random import random

from geohash_hilbert import decode_exactly
from geopip._geo_fkt import bbox, bbox_hash, ccw, in_bbox, p_in_polygon, winding_number
import pytest


################################################################################
################                      bbox                      ##### noqa: E266
################################################################################

def test_has_member():
    assert bbox(dict(bbox=[0, 0, 1, 1])) == [0, 0, 1, 1]


def test_no_poly():
    for type_ in ('Position', 'Point', 'MultiPoint', 'LineString', 'MultiLineString', 'GeometryCollection'):
        with pytest.raises(ValueError):
            bbox(dict(type=type_))


def test_simple_polys(triangle, rect, trapezoid):
    poly = dict(
        type='Polygon',
        coordinates=[
            triangle
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='Polygon',
        coordinates=[
            rect
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='Polygon',
        coordinates=[
            trapezoid
        ]
    )

    assert bbox(poly) == (0, -1, 1, 1)


def test_polys_ignore_holes(triangle):
    poly = dict(
        type='Polygon',
        coordinates=[
            triangle,
            [(0.5, 0.1), (0.75, 0.2), (0.2, 0.2), (0.5, 0.1)]  # valid hole
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='Polygon',
        coordinates=[
            triangle,
            [(1.5, 0.1), (1.75, 0.2), (0.2, -0.2), (1.5, 0.1)]  # invalid hole
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)


def test_simple_multipolys(triangle, rect, trapezoid):
    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            triangle
        ]]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            rect
        ]]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            trapezoid
        ]]
    )

    assert bbox(poly) == (0, -1, 1, 1)


def test_many_simple_multipolys(trapezoid, rect, triangle):
    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            triangle
        ], [
            rect
        ], [
            trapezoid
        ]]
    )

    assert bbox(poly) == (0, -1, 1, 1)


def test_multipolys_ignore_holes():
    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            [(0, 0), (0.5, 1), (1, 0), (0, 0)],  # triangle
            [(1.5, 0.1), (1.75, 0.2), (0.2, -0.2), (1.5, 0.1)]  # invalid hole
        ], [
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],  # Rectangle
            [(0.5, 0.1), (0.75, 0.2), (0.2, 0.2), (0.5, 0.1)]  # valid hole
        ], [
            [(0, 0), (0.5, 1), (1, 0), (0.5, -1), (0, 0)]  # trapezoid
        ]]
    )

    assert bbox(poly) == (0, -1, 1, 1)


################################################################################
################                     in_bbox                    ##### noqa: E266
################################################################################


def test_in_bbox(rect):
    assert in_bbox((0.5, 0.5), (0, 0, 1, 1))  # middle
    assert in_bbox((0, 0.5), (0, 0, 1, 1))  # on left edge
    assert in_bbox((0.5, 0), (0, 0, 1, 1))  # on bottom edge
    assert in_bbox((1, 0.5), (0, 0, 1, 1))  # on right edge
    assert in_bbox((0.5, 1), (0, 0, 1, 1))  # on top edge

    assert in_bbox((0, 0), (0, 0, 1, 1))  # lower left
    assert in_bbox((0, 1), (0, 0, 1, 1))  # upper left
    assert in_bbox((1, 0), (0, 0, 1, 1))  # lower right
    assert in_bbox((1, 1), (0, 0, 1, 1))  # upper right

    assert not in_bbox((0.5, 2), (0, 0, 1, 1))  # above
    assert not in_bbox((0.5, -1), (0, 0, 1, 1))  # below
    assert not in_bbox((-1, 0.5), (0, 0, 1, 1))  # left
    assert not in_bbox((2, 0.5), (0, 0, 1, 1))  # right

    assert not in_bbox((-0.5, -0.5), (0, 0, 1, 1))  # left bottom
    assert not in_bbox((1.5, -0.5), (0, 0, 1, 1))  # right bottom
    assert not in_bbox((-0.5, 1.5), (0, 0, 1, 1))  # left top
    assert not in_bbox((1.5, 1.5), (0, 0, 1, 1))  # right top


################################################################################
################                    bbox_hash                   ##### noqa: E266
################################################################################


def test_bbox_hash(rand_lng, rand_lat):
    for i_ in range(100):
        lng1, lat1 = rand_lng(), rand_lat()
        lng2, lat2 = rand_lng(), rand_lat()

        min_lng = min(lng1, lng2)
        min_lat = min(lat1, lat2)

        max_lng = max(lng1, lng2)
        max_lat = max(lat1, lat2)

        box = (min_lng, min_lat, max_lng, max_lat)

        code = bbox_hash(box)
        lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char=4)

        assert lat - lat_err <= min_lat
        assert lng - lng_err <= min_lng
        assert lat + lat_err >= max_lat
        assert lng + lng_err >= max_lng


################################################################################
################                       ccw                      ##### noqa: E266
################################################################################


def test_ccw():
    assert 0 == ccw((0, 0), (1, 0), (2, 0))  # line from 0,0 to 2,0
    assert 0 > ccw((0, 0), (1, 1), (2, 0))  # middle point above / left of line 0,0 to 2,0
    assert 0 < ccw((0, 0), (1, -1), (2, 0))  # middle point below / right of line 0,0 to 2,0


################################################################################
################                 winding_number                 ##### noqa: E266
################################################################################


def test_winding_number_rect(rect, rand_lat, rand_lng):
    rect_cw = list(reversed(rect))

    # inside
    for i_ in range(100):
        p = (random(), random())
        assert 0 != winding_number(p, rect)
        assert 0 != winding_number(p, rect_cw)
        assert winding_number(p, rect) == -winding_number(p, rect_cw)

    # outside
    for i_ in range(100):
        p = (rand_lng(), rand_lat())
        if not (0 <= p[0] <= 1 and 0 <= p[1] <= 1):
            assert 0 == winding_number(p, rect)
            assert 0 == winding_number(p, rect_cw)


def test_winding_number_star(star, rand_lat, rand_lng):
    star_cw = list(reversed(star))

    # inside
    for i_ in range(100):
        p = (random() * 0.0697 - 0.0257, random() * 0.0383 - 0.016)  # in center of star
        assert 0 != winding_number(p, star)
        assert 0 != winding_number(p, star_cw)
        assert winding_number(p, star) == -winding_number(p, star_cw)

    # top star
    p = (0.006866455078125, 0.06454466408274376)
    assert 0 != winding_number(p, star)
    assert 0 != winding_number(p, star_cw)
    assert winding_number(p, star) == -winding_number(p, star_cw)

    # bottom right
    p = (0.039825439453125, -0.034332273336096036)
    assert 0 != winding_number(p, star)
    assert 0 != winding_number(p, star_cw)
    assert winding_number(p, star) == -winding_number(p, star_cw)

    # left
    p = (-0.0501251220703125, 0.008926391565455)
    assert 0 != winding_number(p, star)
    assert 0 != winding_number(p, star_cw)
    assert winding_number(p, star) == -winding_number(p, star_cw)

    # outside
    box = bbox(dict(type='Polygon', coordinates=[star]))
    for i_ in range(100):
        p = (rand_lng(), rand_lat())
        if not in_bbox(p, box):
            assert 0 == winding_number(p, star)
            assert 0 == winding_number(p, star_cw)


################################################################################
################                  p_in_polygon                  ##### noqa: E266
################################################################################


def test_p_in_polygon_rect(rect, rand_lat, rand_lng):
    rect_cw = [list(reversed(rect))]
    rect = [rect]

    # inside
    for i_ in range(100):
        p = (random(), random())
        assert p_in_polygon(p, rect)
        assert p_in_polygon(p, rect_cw)

    # outside
    for i_ in range(100):
        p = (rand_lng(), rand_lat())
        if not (0 <= p[0] <= 1 and 0 <= p[1] <= 1):
            assert not p_in_polygon(p, rect)
            assert not p_in_polygon(p, rect_cw)


def test_p_in_polygon_rect_w_hole(rect):
    hole = [(0.5, 0.1), (0.2, 0.2), (0.75, 0.2), (0.5, 0.1)]  # cw
    rect_cw = [list(reversed(rect)), list(reversed(hole))]
    rect = [rect, hole]

    # in hole
    assert not p_in_polygon((0.5, 0.15), rect)
    assert not p_in_polygon((0.5, 0.15), rect_cw)

    # in poly, not in hole
    assert p_in_polygon((0.75, 0.3), rect)
    assert p_in_polygon((0.75, 0.3), rect_cw)


def test_p_in_polygon_star(star, rand_lat, rand_lng):
    star_cw = [list(reversed(star))]
    star = [star]

    # inside
    for i_ in range(100):
        p = (random() * 0.0697 - 0.0257, random() * 0.0383 - 0.016)  # in center of star
        assert p_in_polygon(p, star)
        assert p_in_polygon(p, star_cw)

    # top star
    p = (0.006866455078125, 0.06454466408274376)
    assert p_in_polygon(p, star)
    assert p_in_polygon(p, star_cw)

    # bottom right
    p = (0.039825439453125, -0.034332273336096036)
    assert p_in_polygon(p, star)
    assert p_in_polygon(p, star_cw)

    # left
    p = (-0.0501251220703125, 0.008926391565455)
    assert p_in_polygon(p, star)
    assert p_in_polygon(p, star_cw)

    # outside
    box = bbox(dict(type='Polygon', coordinates=star))
    for i_ in range(100):
        p = (rand_lng(), rand_lat())
        if not in_bbox(p, box):
            assert not p_in_polygon(p, star)
            assert not p_in_polygon(p, star_cw)
