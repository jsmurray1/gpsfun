import pytest
from datetime import timedelta
from gpsfun.readers import gpsbabel
from gpsfun.tracks import Track

from readers import gpsbabel, gpx, tcx
from tracks import Track

@pytest.fixture
def tracks_1():
    """
    This is the activity on garmin connect
    https://connect.garmin.com/modern/activity/5014648803

    Metric, computed, Garmin connect
    ELEVATION
    'min_elevation': 1881.0, 1881
    'max_elevation': 2402.4, 2402
    'avg_elevation': 2147.082558643611,
    'ascent': 1919.7999999999963, 1664
    'descent': -1907.9999999999961, 1652

    DISTANCE
    'total_distance': 85485.77194022556, 84.73

    TIME
    'start_time': Timestamp('2020-05-30 14:14:13'), Timestamp('2020-05-30 14:14:13')
    'end_time': Timestamp('2020-05-30 20:00:13'),
    'elapsed_duration': Timedelta('0 days 05:46:00'), Timedelta('0 days 05:46:00')
    'activity_time': Timedelta('0 days 05:46:00'), Timedelta('0 days 05:46:00')
    'moving_time': Timedelta('0 days 05:27:10'), Timedelta('0 days 05:04:09')
    """
    {'min_elevation': 1881.0,
    'max_elevation': 2402.4,
    'avg_elevation': 2147.082558643611,
    'ascent': 1919.7999999999963,
    'descent': -1907.9999999999961,
    'total_distance': 85485.77194022556,
     'start_time': timestamp('2020-05-30 14:14:13'),
     'end_time': timestamp('2020-05-30 20:00:13'),
     'elapsed_duration': timedelta('0 days 05:46:00'),
     'activity_time': timedelta('0 days 05:46:00'),
     'moving_time': timedelta('0 days 05:27:10')}

def test_tracks_1_gpx():
    activityfile = "../tests/test_data/gpx/test_gpx_1.gpx"
    df = gpx(activityfile)
    t = Track(df=df)
    elev = t.elevation()
    assert elev['min_elevation'] == pytest.approx(1881.0, .1)
    assert elev['max_elevation'] == pytest.approx(2402.4, .1)
    assert elev['avg_elevation'] == pytest.approx(2147.082558643611, .1)
    assert elev['ascent'] == pytest.approx(1919.7999999999963, .1)
    assert elev['descent'] == pytest.approx(-1907.9999999999961, .1)
    dist = t.distance()
    assert dist['total_distance'] == pytest.approx(85485.77194022556, .1)
    ti = t.time()
    assert ti['elapsed_duration'] == timedelta(hours=5, minutes=46, seconds=0)
    assert ti['activity_time'] == timedelta(hours=5, minutes=46, seconds=0)
    # assert ti['moving_time'] == timedelta(hours=5, minutes=27, seconds=10)
    assert ti['moving_time'] == timedelta(hours=5, minutes=22, seconds=0)

def test_tracks_1_tcx():
    activityfile = "../tests/test_data/tcx/test_tcx_1.tcx"
    df = tcx(activityfile)
    t = Track(df=df)
    elev = t.elevation()
    assert elev['min_elevation'] == pytest.approx(1881.0, .1)
    assert elev['max_elevation'] == pytest.approx(2402.4, .1)
    assert elev['avg_elevation'] == pytest.approx(2147.082558643611, .1)
    assert elev['ascent'] == pytest.approx(1919.7999999999963, .1)
    assert elev['descent'] == pytest.approx(-1907.9999999999961, .1)
    dist = t.distance()
    assert dist['total_distance'] == pytest.approx(85485.77194022556, .1)
    ti = t.time()
    assert ti['elapsed_duration'] == timedelta(hours=5, minutes=46, seconds=0)
    assert ti['activity_time'] == timedelta(hours=5, minutes=46, seconds=0)
    # assert ti['moving_time'] == timedelta(hours=5, minutes=27, seconds=10)
    assert ti['moving_time'] == timedelta(hours=5, minutes=22, seconds=0)


def test_tracks_1_gpsbabel():
    activityfile = "../tests/test_data/tcx/test_tcx_1.tcx"
    df = gpsbabel(activityfile)
    t = Track(df=df)
    elev = t.elevation()
    assert elev['min_elevation'] == pytest.approx(1881.0, .1)
    assert elev['max_elevation'] == pytest.approx(2402.4, .1)
    assert elev['avg_elevation'] == pytest.approx(2147.082558643611, .1)
    assert elev['ascent'] == pytest.approx(1919.7999999999963, .1)
    assert elev['descent'] == pytest.approx(-1907.9999999999961, .1)
    dist = t.distance()
    assert dist['total_distance'] == pytest.approx(85485.77194022556, .1)
    ti = t.time()
    assert ti['elapsed_duration'] == timedelta(hours=5, minutes=46, seconds=0)
    assert ti['activity_time'] == timedelta(hours=5, minutes=46, seconds=0)
    assert ti['moving_time'] == timedelta(hours=5, minutes=27, seconds=10)






