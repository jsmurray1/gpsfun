from math import sqrt
import pandas as pd
from haversine import haversine, Unit
import requests
from scipy.spatial import distance
from readers import gpsbabel

class track(object):
    """
    Assumes WGS84 coordinate system
    Altitude:
    look at this for altitude: https://github.com/tkrajina/srtm.py
    """

    def __init__(self, df):
        self.df = df

    def elevation(self):
        """
        :return: {max:, min:, average:, ascent:, descent:}
        """
        # TODO implement api to get Altitude data if it is not in the data.
        if "Altitude" in self.df.columns:
            self.min_elevation = self.df["Altitude"].min()
            self.max_elevation = self.df["Altitude"].max()
            self.avg_elevation = self.df["Altitude"].mean()
            self.df["altitude_change"] = self.df["Altitude"].diff()  # differance between rows
            self.ascent = self.df[self.df["altitude_change"] > 0][ "altitude_change"].sum()
            self.descent = self.df[self.df["altitude_change"] < 0]["altitude_change"].sum()
            return {
                "min_elevation": self.min_elevation,
                "max_elevation": self.max_elevation,
                "avg_elevation": self.avg_elevation,
                "ascent": self.ascent,
                "descent": self.descent,
            }
        else:
            return None

    def _calc_moving_time(self, method="simple", min_movement=0.05):
        """
        simple: requires a minimum distance value and if the distance moved in 1 sec is less then this, it is not
        counted as moving. The default os 0.05meters is .1 mph, this is assuming time between points is 1 second, which
        might be wrong.
        """
        if method == "simple":
            self.df["moving_time_between"] = self.df["time_between"]
            if 'distance_between' in self.df.columns:
                self.df.loc[self.df["distance_between"] < min_movement, ["moving_time_between"]] = pd.Timedelta(0)
            else:
                self.distance()
                self.df.loc[self.df["distance_between"] < min_movement, ["moving_time_between"]] = pd.Timedelta(0)
            return self.df["moving_time_between"].sum()

    def time(self):
        """
        elapsed_duration: The time between the first and last record.
        activity_time: Total time between points, probably the same asn elapsed_duration
        moving time: there are different methods, now only a very simple method is used
        :return:
        """
        self.start_time = self.df.iloc[0]["Date_Time"]
        self.end_time = self.df.iloc[-1]["Date_Time"]
        self.df["time_between"] = self.df["Date_Time"].diff()
        self.elapsed_duration = self.end_time - self.start_time
        self.activity_time = self.df["time_between"].sum()
        self.moving_time = self._calc_moving_time(method="simple", min_movement=0.05)
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "elapsed_duration": self.elapsed_duration,
            "activity_time": self.activity_time,
            "moving_time": self.moving_time,
        }

    def distance(self):
        """
        :return:
        """
        self.df["shift_Longitude"] = self.df.shift(1)["Longitude"]
        self.df["shift_Latitude"] = self.df.shift(1)["Latitude"]
        # This is the flat distance between points
        self.df["distance_between"] = self.df.apply(
            lambda x: sqrt(
                (haversine((x["Latitude"], x["Longitude"]),
                           (x["shift_Latitude"], x["shift_Longitude"]),unit="m",)** 2
                 + x["altitude_change"] ** 2)),axis=1)
        self.df.drop(['shift_Longitude', 'shift_Latitude'], axis=1)
        self.total_distance = self.df["distance_between"].sum()
        self.df['distance'] = self.df['distance_between'].cumsum()
        return {'total_distance': self.total_distance}

    def place(self, private_token):
        """
        using mapbox, get place name, "where" the ride was.
        see
        https://docs.mapbox.com/api/search/#reverse-geocoding
        :return:
        """
        params = (('access_token', private_token), ('types', 'place'))
        r = requests.get('https://api.mapbox.com/geocoding/v5/mapbox.places/-105.2386,39.4667.json', params=params)
        self.place_info = r.json()
        self.place_name = self.place_info['features'][0]['place_name']
        return r.json()

    def export_lat_lon(self, file_type='JSON'):
        """
        export the latitude and longitude
        :return: file
        """
        if file_type == 'JSON':
            return self.df[['Latitude', 'Longitude']].to_json(orient='table')
        elif file_type == 'csv':
            self.df[['Latitude', 'Longitude']].to_csv()

class segment(object):
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

