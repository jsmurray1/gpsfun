import numpy as np
from datetime import timedelta

class RallyResults(object):
    """
    segments is the rally definition
    dataframe
    """
    def __init__(self, df, segments):
        self.df = df
        self.init_columns = df.columns
        self.segments = segments
        self.epsilon = 0.00001 # used to for finding acute triangles
        self.near = .0001
        self.results = {}
        # self.ck_points = pd.DataFrame([p['location'] for p in segments], columns=['Latitude', 'Longitude'])
        self.ck_points = [p['location'] for p in segments]
        if not 'shift_Longitude' in self.df.columns:
            self.df['shift_Longitude'] = self.df.shift(-1)['Longitude']
        if not 'shift_Latitude' in self.df.columns:
            self.df['shift_Latitude'] = self.df.shift(-1)['Latitude']
        if not 'dist_to_next' in self.df.columns:
            self.df['dist_to_next'] = np.linalg.norm(self.df[['Latitude', 'Longitude']].values -
                                     self.df[['shift_Latitude', 'shift_Longitude']].values, axis=1)

    def match_checkpoints(self):
        """
        Identify the activity point the represents the arrival at the checkpoint
        find near points that form acute triangles
        :arg
        """
        self.df['to_next'] = np.linalg.norm(self.df[['Latitude', 'Longitude']].values -
                                             self.df[['shift_Latitude', 'shift_Longitude']].values, axis=1)
        self.df['checkpoint'] = np.nan
        for i, ck in enumerate(self.ck_points):
            self.df[f'ck_to_A{i}'] = np.linalg.norm(self.df[['Latitude', 'Longitude']].values - ck, axis=1)
            self.df[f'ck_to_B{i}'] = np.linalg.norm(self.df[['shift_Latitude', 'shift_Longitude']].values - ck, axis=1)
            self.df['acute'] = self.df[f'ck_to_A{i}'] ** 2 + self.df['to_next'] ** 2 <= self.df[f'ck_to_B{i}'] ** 2 + self.epsilon
            self.df.loc[self.df[(self.df[f'ck_to_A{i}'] <= .0001) & (self.df.acute)].index[0], ['checkpoint']] = i
            self.df['seg_time'] = self.df[self.df.checkpoint >= 0]['Date_Time'].diff()

        self.df['segment'] = self.df.checkpoint.fillna(method='ffill')
        self.df['segment'][self.df.segment >= len(self.ck_points)-1] = np.nan

    def calc_results(self):
        """
        calculate and return results
        """
        total_stopwatch = timedelta(seconds=0)
        for i, s in enumerate(self.segments[:-1]):
            stopwatch = self.df.loc[self.df.checkpoint == i + 1]['seg_time'].to_list()[0]
            date_time = self.df.loc[self.df.checkpoint == i]['Date_Time'].to_list()[0]
            self.segments[i]['stopwatch'] = stopwatch
            self.segments[i]['date_time'] = date_time
            if 'timed' in s['type'].keys():
                total_stopwatch = total_stopwatch + stopwatch
                self.segments[i]['total_stopwatch'] = total_stopwatch
            else:
                self.segments[i]['total_stopwatch'] = total_stopwatch

        date_time = self.df.loc[self.df.checkpoint == (len(self.segments) - 1)]['Date_Time'].to_list()[0]
        self.segments[-1]['stopwatch'] = None
        self.segments[-1]['date_time'] = date_time
        self.segments[-1]['total_stopwatch'] = total_stopwatch

        return self.segments











# class Segment(object):
#     """
#     Work in progress
#     """
#     def point_to_line(self, lp1, lp2, p):
#         """
#         Does a perpendicular line from a point to a line intersect between two points.
#         TODO: Consider using shapely https://pypi.org/project/Shapely/
#         """
#         s1 = (lp2[1] - lp1[1])/(lp2[0] - lp1[0])
#         s2 = 1/s1
#         #y1 = s1(x − lp1[0]) + lp1[1]
#         #y2 = s2(x - p[0]) + p[1]
#         x = ((-s1 * lp1[0]) + lp1[1] + s2 * p[0] - p[1]) / (s2 - s1)
#         y = s1 * (x - lp1[0]) + lp1[1]
#         between = (lp2[0] < x < lp1[0]) or (lp2[0] > x > lp1[0]) and (lp2[1] < y < lp1[1]) or (lp2[1] > y > lp1[1])
#         distance = sqrt((p[0] - x)**2 + (p[1] - y)**2)
#
#     def point_to_point(self):
#         df1 = gpsbabel("../tests/test_data/segment_test_1a.gpx")[['Latitude', 'Longitude']]
#         df2 = gpsbabel("../tests/test_data/segment_test_1b.gpx")[['Latitude', 'Longitude']]
#
#         a = distance.cdist(df1, df2, 'euclidean')
#         # b = a[a < .00001]
