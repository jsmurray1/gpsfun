import os
import pandas as pd
import subprocess
import tempfile
from pathlib import Path
import xmltodict
import fitdecode
import col


def _gpsbabel_proc(cmd, infile, outfile):
    process = subprocess.Popen(
        ['gpsbabel', '-t', '-i', f"{cmd}", '-f', infile, '-o', 'unicsv', '-F', outfile],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

def gpsbabel(in_file, file_ext=None):
    """
    gpsbabel -t -i garmin_fit -f {fit_file} -o unicsv -F {csv_file}
    gpsbabel -t -i gpx -f {gpx_file} -o unicsv -F {csv_file}
    gpsbabel -t -i gtrnctr -f {tcx_file} -o unicsv -F {csv_file}
    TODO Consider dealing with zip files of each
    """
    file_cmd = {'.gpx': 'gpx', '.fit': 'garmin_fit', '.tcx': 'gtrnctr'}
    if isinstance(in_file, str): # If it is a str, assume this means it is a path
        file_ext = file_ext or Path(in_file).suffixes[-1].lower()
        with open(in_file, 'rb') as file_obj:
            with tempfile.TemporaryDirectory() as temp_csv_path:
                csv_file_path = os.path.join(temp_csv_path, 'gps_file.csv')
                _gpsbabel_proc(file_cmd[file_ext], in_file, csv_file_path)
                # TODO: check the errors here
                try:
                    df = pd.read_csv(csv_file_path, parse_dates=[['Date', 'Time']])
                except:
                    # TODO Need to check if there are dates
                    df = pd.read_csv(csv_file_path)
    else: # assume it is a file object type
        file_ext = file_ext or Path(in_file.name).suffixes[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False) as temp_gps:
            temp_gps.write(in_file.read())
            in_file.seek(0)
            temp_gps.close()
            with tempfile.TemporaryDirectory() as temp_csv_path:
                csv_file_path = os.path.join(temp_csv_path, 'gps_file.csv')
                _gpsbabel_proc(file_cmd[file_ext], temp_gps.name, csv_file_path)
                # TODO: check the errors here
                try:
                    df = pd.read_csv(csv_file_path, parse_dates=[['Date', 'Time']])
                except:
                    # TODO Need to check if there are dates
                    df = pd.read_csv(csv_file_path)
    return df

def tcx(tcxfile):
    '''
    Using xmltodict
    '''
    df = pd.DataFrame()
    with open(tcxfile, 'rb') as t:
        tcx = xmltodict.parse(t) # This is slow
    assert 'TrainingCenterDatabase' in tcx.keys()
    activity = tcx['TrainingCenterDatabase']['Activities']['Activity']
    # sport = activity['@Sport'] or None
    # Id = activity['Id'] or None
    # creator = activity['Creator'] or None
    laps = activity['Lap']
    # TODO Parse lap metrics
    if isinstance(laps, list):
        all_track_points = []
        for n, l in enumerate(laps):
            for t in l['Track']['Trackpoint']:
                t['lap'] = n
                all_track_points.append(t)
        df = pd.DataFrame(all_track_points)
    elif isinstance(laps, dict):
        df = pd.DataFrame(laps['Track']['Trackpoint'])
    # TODO, seperate the location and other columns
    df = pd.concat([df, pd.json_normalize(df['Position'])], axis=1)
    try:
        df = pd.concat([df, pd.json_normalize(df['Extensions'])], axis=1)
    except:
        # TODO log this
        pass
    try:
        df_temp = pd.json_normalize(df['HeartRateBpm'])
        df_temp.rename(columns=col.tcx_heartate, inplace=True)
        df = pd.concat([df, df_temp], axis=1)
    except:
        # TODO log this
        pass
    df.rename(columns=col.txc_names, inplace=True)
    df["Altitude"] = pd.to_numeric(df["Altitude"], downcast="float")
    df["Latitude"] = pd.to_numeric(df["Latitude"], downcast="float")
    df["Longitude"] = pd.to_numeric(df["Longitude"], downcast="float")
    return df


def gpx(gpxfile):
    """
    Not sure how laps are saved
    """
    with open(gpxfile, 'rb') as g:
        gpx = xmltodict.parse(g)
    df = pd.DataFrame(gpx['gpx']['trk']['trkseg']['trkpt'])
    try:
        df = pd.concat([df, pd.json_normalize(df['extensions'])], axis=1)
        df.rename(columns=col.gpx_extentions, inplace=True)
    except:
        # TODO log this
        pass
    df.rename(columns=col.gpx_names, inplace=True)
    df["Altitude"] = pd.to_numeric(df["Altitude"], downcast="float")
    df["Latitude"] = pd.to_numeric(df["Latitude"], downcast="float")
    df["Longitude"] = pd.to_numeric(df["Longitude"], downcast="float")
    return df

def fit(file):
    """
    https://github.com/polyvertex/fitdecode
    """

    ######
    # incomplete and misc
    ######

    def get_fit_session(fit_json):
        """
        Get activity sessions from fit_json. We are assuming there is 1.
        If there is more then one, we should log an error and use only the first.
        """
        # activity_sessions = []
        # activity_session = None
        # for obj in data:
        #     if obj['frame_type'] == 'data_message' and obj['name'] == 'session':
        #         activity_sessions.append(obj)
        # if len(activity_sessions) == 1:
        #     activity_session = activity_sessions[0]
        # elif len(activity_sessions) < 1:
        #     # log no session found
        #     pass
        # elif len(activity_sessions) > 1:
        #     # TODO log more then one session found. We still choose the first
        #     activity_session = activity_sessions[0]
        #
        # # lets make the list of field easier to use.
        # activity_summary = dict()
        # for f in activity_session['fields']:
        #     activity_summary[f['name']] = {k: v for k, v in f.items() if k != 'name'}
        # return activity_summary
