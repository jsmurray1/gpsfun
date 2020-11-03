#!/usr/bin/env python

"""Basic functional Tests for `gpsfun` package."""

import pytest
import unittest
from pathlib import Path
from gpsfun.readers import tcx, gpx, gpsbabel
from gpsfun.tracks import Track
from gpsfun.rallystyle import RallyResults


@pytest.fixture
def all_files():
    parent_dir = Path(__file__).parent
    p = parent_dir.joinpath('test_data').glob('**/*')
    return [x for x in p if x.is_file() and x.name[:5] == 'test_']


def test_gpsbabel_basic(all_files):
    for f in all_files:
        if f.suffix in ['.tcx', '.gpx', '.fit']:
            df = gpsbabel(str(f))
            assert {'Latitude', 'Longitude', 'Date_Time'}.intersection(set(df.columns)) == \
                   {'Latitude', 'Longitude', 'Date_Time'}, f"failing file: {str(f)}"

def test_gpsbabel_compressed(all_files):
    files = [x for x in all_files if x.suffix in ['.gz', '.zip']]
    for f in files:
        df = gpsbabel(str(f))
        assert {'Latitude', 'Longitude', 'Date_Time'}.intersection(set(df.columns)) == \
               {'Latitude', 'Longitude', 'Date_Time'}, f"failing file: {str(f)}"

def test_gpsbabel_stream(all_files):
    files = [x for x in all_files if x.suffix in ['.tcx', '.gpx', '.fit']]
    for f in files:
        with open(f, 'rb') as f:
            df = gpsbabel(f)
            assert {'Latitude', 'Longitude', 'Date_Time'}.intersection(set(df.columns)) == \
                   {'Latitude', 'Longitude', 'Date_Time'}, f"failing file: {str(f)}"



def test_gpx_tracks(all_files):
    """
    uses gpx not gpsbabel
    """
    assert len(all_files) > 0
    for f in all_files:
        if f.suffix == '.gpx':
            t = Track(df=gpx(f))
            t.elevation()
            assert t.avg_elevation != 0, f"failing file: {str(f)}"
            t.distance()
            assert t.total_distance > 0, f"failing file: {str(f)}"
            t.time()
            assert t.start_time < t.end_time, f"failing file: {str(f)}"


def test_tcx_tracks(all_files):
    '''
    uses tcx not gpsbabel
    '''
    for f in all_files:
        if f.suffix == '.tcx':
            t = Track(df=tcx(f))
            t.elevation()
            assert t.avg_elevation >= 0, f"failing file: {str(f)}"
            t.distance()
            assert t.total_distance > 0, f"failing file: {str(f)}"
            t.time()
            assert t.start_time < t.end_time, f"failing file: {str(f)}"


@pytest.fixture
def roubaix():
    return [{'Segment_name':'Ride Start: lap 1',
            'location': {'lat': 40.117348, 'lon': -105.258836},
            'type_name': 'transport',
            'type_args': {'timed': None}
            },
          {'Segment_name':'End lap 1, Refuel, ride to start',
            'location': {'lat': 40.116263, 'lon': -105.257817},
            'type_name': 'transport',
            'type_args': {'timed': None},
            },
           {'Segment_name':'Race: Lap two',
            'location': {'lat': 40.117348, 'lon': -105.258836},
            'type_name': 'timed',
            'type_args': None,
           },
             {'Segment_name':'Finish',
            'location': {'lat': 40.116263, 'lon': -105.257817},
            'type': 'end'
             }
           ]

@pytest.fixture
def rally_files():
    parent_dir = Path(__file__).parent
    p = parent_dir.joinpath('test_data/rallystyle/roubaix').glob('**/*')
    return [x for x in p if x.is_file() and x.suffix.lower() in ['gpx', 'fit', 'tcx']]

def test_rallystyle_basic(rally_files, roubaix):
    for f in rally_files:
        rs = RallyResults(df = Track(gpsbabel(str(f))).df, segments = roubaix)
        try:
            rs.match_checkpoints()
        except:
            print(f.name)
            raise

        rs.calc_results()

if __name__ == '__main__':
    unittest.main()
