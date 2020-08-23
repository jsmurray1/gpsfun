"""Mostly fuctions used elsewere"""

def increase_points(df, freq='250L', slice=(None,None), columns=None):
    """
    TODO WORK IN PROGRESS
    Need to be carefull and only include columns that it is meaningfull to interpilate between
    freq: 250L is 250 milliseconds
    Columns: you need to be sure the columns are not cumulative or is some other way derived from other when interpilating.
    :param df:
    :return:
    """
    if columns == None:
        columns = ['Date_Time', 'Latitude', 'Longitude', 'Altitude']
    df1 = df[columns][100:200].copy()
    # TODO if we are only using Date_Time as the index then this is not needed.
    df1.set_index(pd.DatetimeIndex(df1['Date_Time']), drop=True, inplace=True)
    df1.drop('Date_Time', axis=1, inplace=True)
    # df1.reset_index(drop=True, inplace=True)
    print(df1[9:13].head(25))

    ups = df1[10:20].resample('250L').asfreq().interpolate(method='linear', limit_direction='forward', axis=0)
    df1 = df1.append(ups)
    df1.sort_index(inplace=True)
    # df1.reset_index(drop=True, inplace=True)

    print(df1[9:20].head(25))
