import dbInserts
import accessDB
import sys
from datetime import datetime

#Attempt converting dateStr to either the full time format with an hour, or just w days
def validateDatetimeFormat(dateStr):
    try:                
        return datetime.strptime(dateStr,"%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:             
            return datetime.strptime(dateStr,"%Y-%m-%d")
        except ValueError:
            return dateStr #COuld return anthing really...

def getKey(tableRow):
    return tableRow[0]


def outputQueryFetchall(cur):
    header = [i[0] for i in cur.description]
    return {'rows': cur.fetchall(), 'header': header}

def runAndOutput(db, query):
    cur = db.cursor()
    cur.execute(query)
    return outputQueryFetchall(cur)


def getNewestEntryInDB(db):
    query = '''SELECT * FROM `Plays` WHERE 1
              ORDER BY `id` DESC
              LIMIT 1'''
    return runAndOutput(db, query)


def getOldestEntryInDB(db):
    query = '''SELECT * FROM `Plays` WHERE 1
              ORDER BY `id` ASC
              LIMIT 1'''
    return runAndOutput(db, query)


def getEntryforRow(queryOut, entry, row=0):
    entryPos = queryOut['header'].index(entry) # find index of anything in the header row
    return queryOut['rows'][row][entryPos] if entryPos != -1 else "null" #return that id


def songsByArtistInPeriod(db, artist=0, startTime=0, endTime=0):
    query = "SELECT DISTINCT * FROM `Plays`"

    filters = []

    # Create filters for those that were entered (0 is just a sentinel)
    if artist != 0:
        filters.append("`artist` = \'" + artist + "\'")

    if startTime != 0:
        # Strip the microseconds
        startTime = startTime.strftime("%Y-%m-%d %H:%M:%S")
        filters.append("`time` > \'" + startTime + "\'")

    if endTime != 0:
        # Strip the microseconds
        endTime = endTime.strftime("%Y-%m-%d %H:%M:%S")
        filters.append("`time` < \'" + endTime + "\'")

    # Add the filters that were there
    for i in xrange(0, len(filters)):
        if i == 0:
            query += " WHERE "

        query += filters[i]
        query += " AND "

    query = query[:query.rfind(" AND ")]  # clip the trailing AND

    print (">> running this query: ", query)

    return runAndOutput(db, query)

def topSongsInPeriod(db, topN=0, startTime=0, endTime=0):

    query = """SELECT `artist`, `song`, COUNT(*) count FROM `Plays` """ 
        #"""WHERE `time` > '2015-11-22' AND `time` < '2015-11-29'
        
    filters = []    

    if startTime != 0:
        # Strip the microseconds
        startTime = startTime.strftime("%Y-%m-%d %H:%M:%S")
        #filters.append("`time` > \'" + startTime + "\'")
        query += "`time` > \'" + startTime + "\' AND"

    if endTime != 0:
        # Strip the microseconds
        endTime = endTime.strftime("%Y-%m-%d %H:%M:%S")
        #filters.append("`time` < \'" + endTime + "\'")
        query += "`time` < \'" + endTime + "\' AND "

     # Add the filters that were there
    # for i in xrange(0, len(filters)):
    #     if i == 0:
    #         query += " WHERE "

    #     query += filters[i]
    #     query += " AND "

    query = query[:query.rfind(" AND ")]  # clip the trailing AND

    query += """ GROUP BY `song` ORDER BY count DESC """
        
    if topN != 0:
        query += """LIMIT 0,""" + str(topN)

    print (">> running this query: ", query)

    return runAndOutput(db, query)

# ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** ~~ ** #

def runQuery(query=[]):

    if len(query) > 1:

        db = accessDB.accessDatabase()

        output = []

        if query[0] == "ARTIST_ANDOR_TIME":
            try:
                # Try and find args and values in the argv
                try:
                    artistIdx = query.index("-artist")
                    artistName = query[artistIdx + 1]
                except:
                    artistName = 0

                try:
                    startTimeIdx = query.index("-start")
                    startTime = query[startTimeIdx + 1]
                except:
                    startTime = 0

                try:
                    endTimeIdx = query.index("-end")
                    endTime = query[endTimeIdx + 1]
                except:
                    endTime = 0

                output = songsByArtistInPeriod(db, artist=artistName, startTime=startTime, endTime=endTime)
                print output

            except Exception,e:
                print "Query 'ARTIST_ANDOR_TIME' takes -artist -start & -end arguments... have fun!"
                print e

        if query[0] == "TOP_N_IN_TIME":
            try:
                # Try and find args and values in the argv
                try:
                    topNIdx = query.index("-topN")
                    topN = query[topNIdx + 1]
                except:
                    topN = 20 # a default value
                try:
                    startTimeIdx = query.index("-start")
                    startTime = query[startTimeIdx + 1]
                except:
                    startTime = 0

                try:
                    endTimeIdx = query.index("-end")
                    endTime = query[endTimeIdx + 1]
                except:
                    endTime = 0

                output = topSongsInPeriod(db, count=topN, startTime=startTime, endTime=endTime)
                print output
            
            except Exception,e:
                print "Query 'TOP_N_IN_TIME' takes -countN -start & -end arguments... get emmmm"
                print e

        else:
            print query[0], " is not a recognised query.."

        accessDB.closeConnection(db)

    else:
        print "I can't do a damn thing if you dont tell me what you want to do"

    return output

if __name__ == "__main__":
    runQuery(sys.argv[1:]) # Run the argv but strip out the file name in position 0 //SORT THIS OUT
    # db = accessDB.accessDatabase()
    # lol = topSongsInPeriod(db, 200)
    # for row in lol['rows']: 
    #     print row
    # # query = "SELECT `artist`, COUNT(*) AS 'Count' FROM `Plays` GROUP BY `artist` SORT BY `Count` LIMIT 30"
    # db = accessDB.accessDatabase()
    # print runAndOutput(db, query)