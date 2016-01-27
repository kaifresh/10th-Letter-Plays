import MySQLdb
import accessDB



def insertPlay(db, song, artist, datetime):
    cur = db.cursor()

    try:
        cur.execute("INSERT INTO `jplay`.`Plays` (`song`, `artist`, `time`) VALUES ('" + song + "', '" + artist + "', '" + datetime.strftime('%Y-%m-%d %H:%M:%S') + "')")
        db.commit()
    except:
        db.rollback()


def batchInsert(db, parsedTweets):

    print "\n~ ~ Batch Insert Tweets ~ ~\n"
    #Format tha twetz
    rows = []

    for tweet in parsedTweets:
        rows.append((tweet['song'],
                     tweet['artist'],
                     tweet['feat'],
                     tweet['raw'],
                     tweet['time'],
                     tweet['created_at'],
                     tweet['id']))

    insertInto = """INSERT INTO  `jplay`.`Plays` (`song` , `artist` ,`feat` ,`raw` ,`time` ,`created_at`, `id`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `duplicate`=1""" 
                    #ON DUPLICATE KEY UPDATE - is a little guard to prevent duplicates...
    cur = db.cursor()
    try:
        cur.executemany(insertInto, rows)
        db.commit()
        print "successfully inserted plays into DB"
    except Exception,e:
        db.rollback()
        print "DID NOT insert plays into DB ", e

# ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **
if __name__ == "__main__":
    print "There is no main..."