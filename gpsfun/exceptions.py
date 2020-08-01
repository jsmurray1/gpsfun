class GPSFunException(Exception):
    pass


class GPSBabelException(GPSFunException):
    pass


####
# RallyStyle
####
class RallyStyleException(GPSFunException):
    def __init__(self, df):
        self.dfcolumns = df.columns
        self.message = f"Dataframe must contains columns:\n{self.dfcolumns}"
        super().__init__(self.message)


class RallyResultsException(RallyStyleException):
    pass


class MatchCheckpointsException(RallyResultsException):
    def __init__(self, df):
        self.df = df
        self.message = f"Dataframe comlumns:\n{self.df.columns}"
        super().__init__(self.message)


class CalcResultsException(RallyResultsException):
    pass
