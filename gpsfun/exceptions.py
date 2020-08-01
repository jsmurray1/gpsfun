class GPSFunException(Exception):
    pass


class GPSBabelException(GPSFunException):
    pass


####
# RallyStyle
####
class RallyStyleException(GPSFunException):
    pass


class RallyResultsException(RallyStyleException):
    pass


class MatchCheckpointsException(RallyResultsException):
    pass


class CalcResultsException(RallyResultsException):
    pass
