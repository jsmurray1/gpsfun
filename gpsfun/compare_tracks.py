#See https://github.com/vincentdavis/cmpgpx

import numpy

def align_tracks(track1, track2, gap_penalty):
    """ Needleman-Wunsch algorithm adapted for gps tracks. """

    _log.info("Aligning tracks")

    def similarity(p1, p2):
        d = gpxpy.geo.distance(p1.latitude, p1.longitude, p1.elevation,
                               p2.latitude, p2.longitude, p2.elevation)
        return -d

    # construct f-matrix
    f = numpy.zeros((len(track1), len(track2)))
    for i in range(0, len(track1)):
        f[i][0] = gap_penalty * i
    for j in range(0, len(track2)):
        f[0][j] = gap_penalty * j
    for i in range(1, len(track1)):
        t1 = track1[i]
        for j in range(1, len(track2)):
            t2 = track2[j]
            match = f[i-1][j-1] + similarity(t1, t2)
            delete = f[i-1][j] + gap_penalty
            insert = f[i][j-1] + gap_penalty
            f[i, j] = max(match, max(delete, insert))

    # backtrack to create alignment
    a1 = []
    a2 = []
    i = len(track1) - 1
    j = len(track2) - 1
    while i > 0 or j > 0:
        if i > 0 and j > 0 and \
           f[i, j] == f[i-1][j-1] + similarity(track1[i], track2[j]):
            a1.insert(0, track1[i])
            a2.insert(0, track2[j])
            i -= 1
            j -= 1
        elif i > 0 and f[i][j] == f[i-1][j] + gap_penalty:
            a1.insert(0, track1[i])
            a2.insert(0, None)
            i -= 1
        elif j > 0 and f[i][j] == f[i][j-1] + gap_penalty:
            a1.insert(0, None)
            a2.insert(0, track2[j])
            j -= 1
    return a1, a2
