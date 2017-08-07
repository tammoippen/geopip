from geopip._geo_fkt import bbox
import pytest


def test_has_member():
    assert bbox(dict(bbox=[0, 0, 1, 1])) == [0, 0, 1, 1]


def test_no_poly():
    for type_ in ('Position', 'Point', 'MultiPoint', 'LineString', 'MultiLineString', 'GeometryCollection'):
        with pytest.raises(ValueError):
            bbox(dict(type=type_))


def test_simple_polys():
    poly = dict(
        type='Polygon',
        coordinates=[
            [(0, 0), (0.5, 1), (1, 0), (0, 0)]  # triangle
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='Polygon',
        coordinates=[
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]  # Rectangle
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='Polygon',
        coordinates=[
            [(0, 0), (0.5, 1), (1, 0), (0.5, -1), (0, 0)]  # trapezoid
        ]
    )

    assert bbox(poly) == (0, -1, 1, 1)


def test_polys_ignore_holes():
    poly = dict(
        type='Polygon',
        coordinates=[
            [(0, 0), (0.5, 1), (1, 0), (0, 0)],  # triangle
            [(0.5, 0.1), (0.75, 0.2), (0.2, 0.2), (0.5, 0.1)]  # valid hole
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='Polygon',
        coordinates=[
            [(0, 0), (0.5, 1), (1, 0), (0, 0)],  # triangle
            [(1.5, 0.1), (1.75, 0.2), (0.2, -0.2), (1.5, 0.1)]  # invalid hole
        ]
    )

    assert bbox(poly) == (0, 0, 1, 1)


def test_simple_multipolys():
    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            [(0, 0), (0.5, 1), (1, 0), (0, 0)]  # triangle
        ]]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]  # Rectangle
        ]]
    )

    assert bbox(poly) == (0, 0, 1, 1)

    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            [(0, 0), (0.5, 1), (1, 0), (0.5, -1), (0, 0)]  # trapezoid
        ]]
    )

    assert bbox(poly) == (0, -1, 1, 1)


def test_many_simple_multipolys():
    poly = dict(
        type='MultiPolygon',
        coordinates=[[
            [(0, 0), (0.5, 1), (1, 0), (0, 0)]  # triangle
        ], [
            [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]  # Rectangle
        ], [
            [(0, 0), (0.5, 1), (1, 0), (0.5, -1), (0, 0)]  # trapezoid
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
