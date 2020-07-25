import numpy as np
from math import sqrt

# Example
# results = {"segments": [{"segment": 1, "Timestamp":0, data: {}},]
# ,"totals": {"total_time": 0, "timed": 0, 'transport': 0}}

results = {"segments": [],
           "totals": {"total_time": None, "timed": None, 'transport': None}
           }

class RallyResults(object):
    """
    segments is the rally definition
    dataframe
    example results:
    results = {"segments": [],
           "totals": {"total_time": None, "timed": None, 'transport': None}
           }
    """
    def __init__(self, df, segments):
        self.df = df
        self.init_columns = df.columns
        self.segments = segments
        self.epsilon = 0.00001 # used to for finding acute triangles
        self.near = .0001
        self.results = {"segments": [],"totals": {"total_time": None, "timed": None, 'transport': None}}
        # self.ck_points = pd.DataFrame([p['location'] for p in segments], columns=['Latitude', 'Longitude'])
        self.ck_points = [p['location'] for p in segments]
        if not 'shift_Longitude' in self.df.columns or not 'shift_Longitude' in self.df.columns:
            self.df['shift_Longitude'] = self.df.shift(-1)['Longitude']
            self.df['shift_Latitude'] = self.df.shift(-1)['Latitude']
            self.df['dist_to_next'] = np.linalg.norm(self.df[['Latitude', 'Longitude']].values -
                                     self.df[['shift_Latitude', 'shift_Longitude']].values, axis=1)

    def match_checkpoints(self):
        """
        Identify the activity point the represents the arrival at the checkpoint
        find near points that form acute triangles
        :arg
        """
        self.df['checkpoint'] = np.nan
        self.df[f'mark'] = False
        for i, p in enumerate(self.ck_points.values):
            self.df[f'p_to_A{i}'] = np.linalg.norm(self.df[['Latitude', 'Longitude']].values - p, axis=1)
            self.df[f'p_to_B{i}'] = np.linalg.norm(self.df[['shift_Latitude', 'shift_Longitude']].values - p, axis=1)
            self.df['acute'] = self.df[f'p_to_A{i}'] ** 2 + self.df['to_next'] ** 2 <= self.df[f'p_to_B{i}'] ** 2 + self.epsilon

            self.df['checkpoint'] = np.nan
            self.df[f'mark_{i}'] = False
            self.df.loc[
            self.df[(self.df[f'p_to_A{i}'] <= self.near) & (self.df.acute)].index[0], ['checkpoint']] = i
            self.df.loc[self.df[(self.df[f'p_to_A{i}'] <= self.near) & (self.df.acute)].index[0], [f'mark_{i}', 'mark']] = True

            seg_result = self.df[self.df[f'mark_{1}']][['Date_Time', 'Latitude', 'Longitude']].iloc[0].to_dict()
            update_results(seg_result, results)

            print('#####')
            print(self.df[[f'p_to_A{i}', f'p_to_B{i}', 'to_next', 'acute', f'mark_{i}', 'mark']][self.df.mark == True])





class Segment(object):
    """
    Work in progress
    """
    def point_to_line(self, lp1, lp2, p):
        """
        Does a perpendicular line from a point to a line intersect between two points.
        TODO: Consider using shapely https://pypi.org/project/Shapely/
        """
        s1 = (lp2[1] - lp1[1])/(lp2[0] - lp1[0])
        s2 = 1/s1
        #y1 = s1(x − lp1[0]) + lp1[1]
        #y2 = s2(x - p[0]) + p[1]
        x = ((-s1 * lp1[0]) + lp1[1] + s2 * p[0] - p[1]) / (s2 - s1)
        y = s1 * (x - lp1[0]) + lp1[1]
        between = (lp2[0] < x < lp1[0]) or (lp2[0] > x > lp1[0]) and (lp2[1] < y < lp1[1]) or (lp2[1] > y > lp1[1])
        distance = sqrt((p[0] - x)**2 + (p[1] - y)**2)

    def point_to_point(self):
        df1 = gpsbabel("../tests/test_data/segment_test_1a.gpx")[['Latitude', 'Longitude']]
        df2 = gpsbabel("../tests/test_data/segment_test_1b.gpx")[['Latitude', 'Longitude']]

        a = distance.cdist(df1, df2, 'euclidean')
        # b = a[a < .00001]
