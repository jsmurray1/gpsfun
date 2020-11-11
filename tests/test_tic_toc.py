#!/usr/bin/env python

"""Rally Style Tests"""

import pytest
from datetime import timedelta
from gpsfun.readers import gpsbabel
from gpsfun.tracks import Track
from gpsfun.tic_toc import TicTocResults

@pytest.fixture
def watopia_waistband():
    return [{'segment_name':'Ride to start',
            'location': {'lat': -11.63508, 'lon': 166.97511},
            'type_name': 'transport',
            'type_args': {'timer': None},
            },
            {'segment_name':'Ride Start',
            'location': {'lat': -11.63518, 'lon': 166.97386},
            'type_name': 'tic_toc',
            'type_args': {'timer': 300}
             },
            ]

def test_tictok_1(watopia_waistband):
    rfile = "test_data/tictoc/2020-10-29-19-10-19.fit"
    activity = Track(gpsbabel(str(rfile)))
    activity.distance()
    rs = TicTocResults(df=activity.df, segments=watopia_waistband)
    rs.calc_results()
    assert rs.results[1]['distance'] == 2358.3245572657142

