import numpy as np

try:
    from .exceptions import RallyStyleException, RallyResultsException, MatchCheckpointsException, CalcResultsException
except:
    from exceptions import RallyStyleException, RallyResultsException, MatchCheckpointsException, CalcResultsException
try:
    from .segments import match_checkpoints, calculate_segment_distance
except:
    from segments import match_checkpoints, calculate_segment_distance


class TicTocResults(object):
    """
    Adding to the rally style segment definitions

    segments: is the tictoc definition
    type_name: STRING "timed", "Transport"
    type_args: DICT, time_limit in sec for transport
    total_timed_types: DICT [gravel, uphill, road, ...]
    Segment structure:
      [{
        'segment_name':'Event Start',
        'location': {'lat': 39.737912, 'lon': -105.523881},
        'type_name': 'tictoc',
        'type_args': {tictoc_time: 30} time is in minutes
        total_timed_types: {'uphill':None(0), 'gravel': None}
      },]

      result structure:
      [{
        'segment_name': 'Event Start',
        'location': {'lat': 39.737912, 'lon': -105.523881},
        'type_name': 'tictoc',
        'type_args': {tictoc_time: 30}
        'duration': Timedelta('0 days 00:30'),
        'datetime': Timestamp('2012-07-21 09:18:13'),
        'total_timed': datetime.timedelta(0),
        total_timed_types: {'uphill':Timedelta(123), 'gravel': Timedelta(321)}
        distance: {23400} # the distance traveled in  time, this is what the results are based on.
      },]
        """

    def __init__(self, df, segments):
        if {'Latitude', 'Longitude', 'Date_Time'}.intersection(set(df.columns)) != {'Latitude', 'Longitude',
                                                                                    'Date_Time'}:
            raise RallyStyleException(f"Dataframe must contains columns: \n {df.columns}")
        self.df = df
        self.init_columns = df.columns
        self.segments = segments
        self.epsilon = 0.00001  # used to for finding acute triangles
        self.near = .0002  # How near the point needs to be to the checkpoint.
        self.results = []
        # self.ck_points = pd.DataFrame([p['location'] for p in segments], columns=['Latitude', 'Longitude'])
        self.ck_points = [p['location'] for p in segments]
        if 'shift_Longitude' not in self.df.columns:
            self.df['shift_Longitude'] = self.df.shift(-1)['Longitude']
        if 'shift_Latitude' not in self.df.columns:
            self.df['shift_Latitude'] = self.df.shift(-1)['Latitude']
        if 'dist_to_next' not in self.df.columns:
            self.df['dist_to_next'] = np.linalg.norm(self.df[['Latitude', 'Longitude']].values -
                                                     self.df[['shift_Latitude', 'shift_Longitude']].values, axis=1)

    def calc_results(self):
        """
        We are assuming only 1 tictoc section. We have a start point that triggers the timer.
        """
        match_checkpoints(df=self.df, epsilon=self.epsilon, near=self.near, segments=self.segments)
        self.results = calculate_segment_distance(self.df, self.segments)
        return self.results

    def export_lat_lon_alt(self, file_type='JSON'):
        """
        export the latitude and longitude
        :return: file
        """
        if file_type == 'JSON':
            return [dict(longitude=r.Longitude, latitude=r.Latitude, altitude=r.Altitude) for r in self.df.itertuples()]
        elif file_type == 'csv':
            self.df[['Latitude', 'Longitude', 'Altitude']].to_csv('export.csv')
