#!/usr/bin/env python

"""Rally Style Tests"""

import pytest
from datetime import timedelta
from gpsfun.readers import gpsbabel
from gpsfun.tracks import Track
from gpsfun.tic_toc import TicTocResults

@pytest.fixture
def watopia_waistband():
    return [{'Segment_name':'Ride to start',
            'location': {'lat': -11.63508, 'lon': 166.97511},
            'type_name': 'transport',
            'type_args': {'timed': None},
            },
            {'Segment_name':'Ride Start',
            'location': {'lat': -11.63518, 'lon': 166.97386},
            'type_name': 'tictoc',
            'type_args': {'tictoc': 5}
             },
            ]

def test_tictok_1(watopia_waistband):
    rfile = "test_data/tictoc/2020-10-29-19-10-19.fit"
    activity = Track(gpsbabel(str(rfile)))
    activity.distance()
    rs = TicTocResults(df=activity.df, segments=watopia_waistband)
    rs.calc_results()

    # assert rs.results[0]['duration'] == timedelta(hours=1, minutes=2, seconds=2)
    # assert rs.results[0]['total_timed'] == timedelta(0)
    # assert rs.results[1]['duration'] == timedelta(hours=0, minutes=0, seconds=33)
    # assert rs.results[1]['total_timed'] == timedelta(0)
    # assert rs.results[2]['duration'].total_seconds() == timedelta(hours=0, minutes=50, seconds=9).total_seconds()
    # assert rs.results[2]['total_timed'].total_seconds() == timedelta(hours=0, minutes=50, seconds=9).total_seconds()
    # assert rs.results[-1]['total_timed'].total_seconds() == timedelta(days=0, minutes=50, seconds=9).total_seconds()
    # assert rs.results[-1]['duration'] == None
