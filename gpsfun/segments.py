from datetime import timedelta
import pandas as pd
import numpy as np

try:
    from .exceptions import MatchCheckpointsException
except:
    from exceptions import MatchCheckpointsException


def find_acute(df, i, segment, near, epsilon):
    """
    1. Calculate the distance from the chekpoint to all consecutive points in the data.
    2. Acute, For ck "i" if the angle between the lines ck:A and A:B acute. If so then ck is "between" A and B
            Epislon is the fudge factor
    """
    point = (segment['location']['lat'], segment['location']['lon'])
    df[f'ck_to_A{i}'] = np.linalg.norm(df[['Latitude', 'Longitude']].values - point, axis=1)
    df[f'ck_to_B{i}'] = np.linalg.norm(df[['shift_Latitude', 'shift_Longitude']].values - point,
                                       axis=1)
    if df[f'ck_to_A{i}'].min() > near * 10:
        raise MatchCheckpointsException(
            f"It appears you never made it close to checkpoint {segment['segment_name']}")
    df['acute'] = df[f'ck_to_A{i}'] ** 2 + df['dist_to_next'] ** 2 <= df[
        f'ck_to_B{i}'] ** 2 + epsilon


def match_checkpoints(df, epsilon, near, segments):
    """
    Identify the activity point the represents the arrival at the checkpoint
    find near points that form acute triangles
    """
    row_slice = 0
    for i, seg in enumerate(segments):
        try:
            find_acute(df, i, seg, near, epsilon)
            # assign segment number to first acute point near the point seg point)
            df.loc[
                df[row_slice:][(df[row_slice:][f'ck_to_A{i}'] <= near) &
                               (df[row_slice:].acute)].index[0], ['checkpoint', 'segment_name']] = i, seg[
                'segment_name']
            # This removes the points we have past.
            row_slice = int(df[df.checkpoint == i].index[0])
            # df['seg_duration'] = df[df.checkpoint >= 0]['Date_Time'].diff()
        except Exception as e:
            raise MatchCheckpointsException(
                f"Fail on checkpoint:{i} location: {(seg['location']['lat'], seg['location']['lon'])}\nDataframe columns:\n{df.columns}")


def calculate_segment_times(df, segments):
    """
    This is for fix distance segments, competing for time
    this selects only rows match to checkpoints. The calcs the diff in time.
    """
    df['seg_duration'] = df[df.checkpoint >= 0]['Date_Time'].diff()
    df['segment'] = df.checkpoint.fillna(method='ffill')
    # Set everything at the end to nan
    df['segment'][df.segment >= len(segments) - 1] = np.nan
    # TODO Add segment metrics


def calculate_segment_distance(df, segments):
    """
    This is for fixed distance competeing for distance TicToc
    [{
    'segment_name': 'Event Start',
    'location': {'lat': 39.737912, 'lon': -105.523881},
    'type_name': 'transport',
    'type_args': {'time_limit': 1800}
    'duration': Timedelta('0 days 00:24:21'),
    'datetime': Timestamp('2012-07-21 09:18:13'),
    'distance': 25677
    'total_timed': datetime.timedelta(0),
     total_timed_types: {'uphill':Timedelta(123), 'gravel': Timedelta(321)}
     },]
     """
    results = []
    for i, seg in enumerate(segments):
        if seg['type_name'] == 'tic_toc':
            seg_start_time = df[df.checkpoint == i].Date_Time.values[0]
            seg_end_time = seg_start_time + pd.Timedelta(seconds=seg['type_args']['timer'])
            seg_past_end = df[df.Date_Time >= seg_end_time].iloc[0]
            seg_before_end = df[df.Date_Time <= seg_end_time].iloc[-1]
            a = seg_before_end.distance
            b = seg_past_end.distance
            c = seg_before_end.Date_Time
            d = seg_past_end.Date_Time
            p = seg_end_time
            seg_finish = (b - a) * ((p - d) / (d - c)) + a
            seg_distance = seg_finish - df[df.checkpoint == i].distance.iloc[0]
            seg['distance'] = seg_distance
            seg['duration'] = timedelta(seconds=seg['type_args']['timer'])
            seg['datetime'] = pd.to_datetime(seg_start_time)
            results.append(seg)
        else:
            results.append(seg)
    return results


def select_near_points(self, check_point, df):
    """
    TODO: Work in progress
    Selects points near the checkpoints:
    These may be anywhere in the activity, but that seems ok.
    """
    df['Date_Time'] = df.Date_Time.astype(np.int64)
    columns = ['Date_Time', 'Latitude', 'Longitude', 'Altitude']
    start = 10
    end = 11
    rows = 7  # actually get rows - 2
    realend = (end - start) * 5 + start
    for i in range(start, realend, rows):
        curr_row = df[columns].iloc[i]
        next_row = df[columns].iloc[i + 1]
        new_df = pd.DataFrame(np.linspace(curr_row, next_row, rows), columns=columns)
        df = pd.concat([df[:i], new_df, df[i + rows:]], ignore_index=True)

    df['Date_Time'] = df.Date_Time.astype('datetime64[ns]')
    print(df[9:25].head(25))
