import os
from random import random

import pytest


@pytest.fixture()
def testdir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def rand_lng():
    return lambda: random() * 360 - 180


@pytest.fixture()
def rand_lat():
    return lambda: random() * 180 - 90


@pytest.fixture()
def triangle():
    return [(0, 0), (0.5, 1), (1, 0), (0, 0)]


@pytest.fixture()
def rect():
    return [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]


@pytest.fixture()
def trapezoid():
    return [(0, 0), (0.5, 1), (1, 0), (0.5, -1), (0, 0)]


@pytest.fixture()
def star():
    return [[0.0034, 0.0981], [-0.026, 0.0226], [-0.083, 0.0144], [-0.028, -0.020],
            [-0.040, -0.069], [0.0082, -0.026], [0.0549, -0.062], [0.0453, -0.010],
            [0.1229, 0.0254], [0.0425, 0.0274], [0.0034, 0.0981]]
