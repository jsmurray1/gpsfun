from math import sqrt
import pandas as pd
from haversine import haversine, Unit
import requests


class Track(object):
    """
    Assumes WGS84 coordinate system
    Altitude:
    look at this for altitude: https://github.com/tkrajina/srtm.py
    """

    def __init__(self, df):
        self.df = df
        self.columns = df.columns
        self.min_elevation = None
        self.max_elevation = None
        self.avg_elevation = None
        self.ascent = None
        self.descent = None
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.activity_time = None
        self.moving_time = None
        self.total_distance = None
        self.place_info = None
        self.place_name = None

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
            self.ascent = self.df[self.df["altitude_change"] > 0]["altitude_change"].sum()
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

    def time(self):
        """
        elapsed_duration: The time between the first and last record.
        activity_time: Total time between points, probably the same asn elapsed_duration
        moving time: there are different methods, now only a very simple method is used
        """
        self.start_time = self.df.iloc[0]["Date_Time"]
        self.end_time = self.df.iloc[-1]["Date_Time"]
        self.df["time_between"] = self.df["Date_Time"].diff()
        self.elapsed_time = self.end_time - self.start_time
        self.activity_time = self.df["time_between"].sum()
        self.moving_time = self._calc_moving_time(method="simple", min_movement=0.05)
        self.mean_gap = self.df["time_between"].mean()
        self.median_gap = self.df["time_between"].median()
        self.max_gap = self.df["time_between"].max()
        self.min_gap = self.df["time_between"].min()

        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "elapsed_duration": self.elapsed_time,
            "activity_time": self.activity_time,
            "moving_time": self.moving_time,
            'mean_gap': self.mean_gap,
            'median_gap': self.median_gap,
            'max_gap': self.max_gap,
            'min_gap': self.min_gap
            }

    def distance(self):
        """
        :return: {'total_distance': self.total_distance}
        """
        if 'altitude_change' not in self.df.columns:
            self.elevation()
        self.df["shift_Longitude"] = self.df.shift(1)["Longitude"]
        self.df["shift_Latitude"] = self.df.shift(1)["Latitude"]
        # This is the flat distance between points
        self.df["distance_between"] = self.df.apply(
            lambda x: sqrt(
                (haversine((x["Latitude"], x["Longitude"]),
                           (x["shift_Latitude"], x["shift_Longitude"]), unit="m",) ** 2
                 + x["altitude_change"] ** 2)), axis=1)
        self.df.drop(['shift_Longitude', 'shift_Latitude'], axis=1)
        self.total_distance = self.df["distance_between"].sum()
        self.df['distance'] = self.df['distance_between'].cumsum()
        self.mean_dist = self.df[self.df.distance_between > 0]["distance_between"].mean()
        self.median_dist = float(self.df[self.df.distance_between > 0]["distance_between"].median())
        self.max_dist = self.df["distance_between"].max()
        self.min_dist = self.df[self.df.distance_between > 0]["distance_between"].min()
        return {'total_distance': self.total_distance,
                'mean_dist': self.mean_dist,
                'median_dist': self.median_dist,
                'max_dist': self.max_dist,
                'min_dist': self.min_dist
                }

    def place(self, private_token):
        """
        using mapbox, get place name, "where" the ride was.
        see
        https://docs.mapbox.com/api/search/#reverse-geocoding
        r = requests.get('https://api.mapbox.com/geocoding/v5/mapbox.places/-105.2386,39.4667.json', params=params)

        TODO Add a retry
        https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
        TODO Log errors
        """
        params = (('access_token', private_token), ('types', 'place'))
        longitude, latitude = self.df.iloc[0][['Longitude', 'Latitude']].values
        try:
            r = requests.get(f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json", params=params)
            self.place_info = r.json()
            self.place_name = self.place_info['features'][0]['place_name']
            return {'place_info': self.place_info, 'place_name': self.place_name}
        except Exception as e:
            return {'place_info': self.place_info, 'place_name': self.place_name}  # The Values should be none

    @property
    def calculate(self):
        """
        Calculate everything
        """
        r = self.elevation()
        r.update(self.distance())
        r.update(self.time())
        return r


    def export_lat_lon_alt(self, file_type='JSON'):
        """
        export the latitude and longitude
        :return: file
        """
        if file_type == 'JSON':
            return [dict(longitude=r.Longitude, latitude=r.Latitude, altitude=r.Altitude) for r in self.df.itertuples()]
        elif file_type == 'csv':
            self.df[['Latitude', 'Longitude']].to_csv('export.csv')

