import itertools

import dbQueries as dbq
import accessDB

def plays(playData=None, startDate=None, endDate=None):
    # db = accessDB.accessDatabase()
    try:
        queryVect = ["ARTIST_ANDOR_TIME", "-artist", str(playData)]

        if startDate != None:
            queryVect.append("-start")
            startDate = dbq.validateDatetimeFormat(startDate)
            queryVect.append(startDate)

        if endDate != None:
            queryVect.append("-end")
            endDate = dbq.validateDatetimeFormat(endDate)
            queryVect.append(endDate)

        output = dbq.runQuery(queryVect)

        data = []
        header = output['header']
        for row in output['rows']:
            curTup = {}
            for i in xrange(0,len(header)):
                curTup[ str(header[i]) ] = str(row[i])

            data.append(curTup)
    except Exception, e:
        print e


lol = 0

plays("rufussounds", "2015-11-25")