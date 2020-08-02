#!/usr/bin/env python

"""Tests for `gpsfun` package."""
#  from gpsfun import gpsfun

import pytest
import unittest
from pathlib import Path
from gpsfun.readers import tcx, gpx, gpsbabel
from gpsfun.tracks import Track


@pytest.fixture
def files():
    parent_dir = Path(__file__).parent
    p = parent_dir.joinpath('test_data').glob('**/*')
    return [x for x in p if x.is_file() and x.name[:5] == 'test_']


def test_gpsbabel_basic(files):
    for f in files:
        if f.suffix in ['.tcx', '.gpx', '.fit']:
            df = gpsbabel(str(f))
            assert {'Latitude', 'Longitude', 'Date_Time'}.intersection(set(df.columns)) == {'Latitude', 'Longitude', 'Date_Time'}


def test_gpx_tracks(files):
    """
    uses gpx not gpsbabel
    """
    assert len(files) > 0
    for f in files:
        if f.suffix == '.gpx':
            t = Track(df=gpx(f))
            t.elevation()
            assert t.avg_elevation != 0
            t.distance()
            assert t.total_distance > 0
            t.time()
            assert t.start_time < t.end_time


def test_tcx_tracks(files):
    '''
    uses tcx not gpsbabel
    '''
    for f in files:
        if f.suffix == '.tcx':
            t = Track(df=tcx(f))
            t.elevation()
            assert t.avg_elevation != 0
            t.distance()
            assert t.total_distance > 0
            t.time()
            assert t.start_time < t.end_time


if __name__ == '__main__':
    unittest.main()
