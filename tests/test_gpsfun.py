#!/usr/bin/env python

"""Tests for `gpsfun` package."""
#  from gpsfun import gpsfun

import pytest
import unittest
from pathlib import Path
from gpsfun.readers import tcx, gpx
from gpsfun.tracks import Track

p = Path(r'test_data').glob('*')
files = [x for x in p if x.is_file()]

def test_basic_txc():
    assert(len(files)) > 0
    for f in files:
        if f.suffix == '.tcx':
            df = tcx(f)
            assert 'Latitude' in df.columns
            assert len(df) > 100
def test_basic_gpx():
    assert (len(files)) > 0
    for f in files:
        if f.suffix == '.gpx':
            df = gpx(f)
            assert 'Latitude' in df.columns
            assert len(df) > 100

def test_gpx_tracks():
    assert (len(files)) > 0
    for f in files:
        if f.suffix == '.gpx':
            t = track(df=gpx(f))
            t.elevation()
            assert t.avg_elevation != 0

def test_tcx_tracks():
    assert (len(files)) > 0
    for f in files:
        if f.suffix == '.tcx':
            t = track(df=tcx(f))
            t.elevation()
            assert t.avg_elevation != 0


if __name__ == '__main__':
    unittest.main()

# @pytest.fixture
# def response():
#     """Sample pytest fixture.
#
#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
#     pass
#
#
# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string
#     pass
