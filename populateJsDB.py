import tweepy
import re
import datetime
import time
import csv
import accessDB
import dbInserts
import dbQueries
import sys
from pytz import timezone
import pytz


def tweets_to_csv(alltweets, title="some"):
    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

    # write the csv
    with open('%s_tweets.csv' % title, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "text"])
        writer.writerows(outtweets)
        f.close()
    pass


def parseTweet(tweet):
    # https://regex101.com/#python
    # Obviously we are just putting faith in the formatting of @tripleJplay
    songRegex = re.compile(r"(?<=-\W).+?(?=\W\[)")
    artistWithTwitterRegex = re.compile(r'(?<=@).+?(?=\W)')  #
    aristWithoutTwitterRegex = re.compile(r'.+(?=\W-)')
    featureArtistTwitterRegex = re.compile(r'(?<=ft.\W\@).+?(?=\W)')
    timeRegex = re.compile(r'(?<=\[)[0-9]{2}:[0-9]{2}(?=\])')  # (?<=\[).+(?=\]) #THIS IS VERY SPECIFIC

    song = songRegex.search(tweet.text)
    artist = artistWithTwitterRegex.search(tweet.text)
    feat = featureArtistTwitterRegex.search(tweet.text)
    time = timeRegex.search(tweet.text)
    day = tweet.created_at.day
    month = tweet.created_at.month
    year = tweet.created_at.year

    if song:
        song = song.group()
    else:
        song = "^Song Not Found!^"

    if artist:
        artist = artist.group()
    else:
        artistNoTwitter = aristWithoutTwitterRegex.search(tweet.text)

        if artistNoTwitter:
            artist = artistNoTwitter.group()
        else:
            artist = "!Artist Not Found!"
    if feat:
        feat = feat.group()
    else:
        feat = '*Feature Artist Not Found*'

    if time:
        time = time.group()
    else:
        time = "%Time Not Found!%"

    #use pytz to put the time in sydney time
    sydney = timezone('Australia/Sydney')
    tweet.created_at = timezone('UTC').localize(tweet.created_at) #Attach UTC time to tweet
    date_object = tweet.created_at.astimezone(sydney) #Convert to sydney time
    date_object = date_object.replace(hour=int(str(time)[:2]), minute=int(str(time)[3:])) #get the hour and minute from the actual tweet

    return {'song': song, 'artist': artist, 'feat': feat, 'time': date_object, 'raw': tweet.text,
            'created_at': tweet.created_at, 'id': tweet.id}


def get_tweets(api, screen_name, limit=0, parseTweets=True):  # asyncSendToDB=False, asyncBatchSize=100):
    allTweets = []

    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items(limit):

        try:
            # You can select the tweet format here
            if parseTweets:
                allTweets.append(parseTweet(tweet))

            else:
                allTweets.append(tweet)

            print allTweets[-1], "\n"

        except tweepy.TweepError:
            print "\n\n\n********************\nHIT THE RATE LIMITER\n************************"
            time.sleep(60 * 15)  # WAIT FOR 15 MINUTES, THEN HAVE ANOTHER CRACK
            continue
        except StopIteration:  # If there's nothing left
            print "\n\n\n********************\nNO MORE TWEEETS\n************************"
            break

    print "tweets extracted....", len(allTweets)
    return allTweets


def get_tweets_before(api, screen_name, max_id, limit=0):
    allTweets = []

    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, max_id=max_id).items(limit):
        try:
            allTweets.append(parseTweet(tweet))
            print allTweets[-1], "\n"

        except tweepy.TweepError:
            print "\n\n\n********************\nHIT THE RATE LIMITER\n************************"
            time.sleep(60 * 15)  # WAIT FOR 15 MINUTES, THEN HAVE ANOTHER CRACK
            continue
        except Exception, e:
            print "Something failed: ", e

    print "tweets extracted....", len(allTweets)
    return allTweets


def get_tweets_after(api, screen_name, since_id, limit=0):
    allTweets = []

    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, since_id=since_id).items(limit):
        try:
            allTweets.append(parseTweet(tweet))
            print allTweets[-1], "\n"

        except tweepy.TweepError:
            print "\n\n\n********************\nHIT THE RATE LIMITER\n************************"
            time.sleep(60 * 15)  # WAIT FOR 15 MINUTES, THEN HAVE ANOTHER CRACK
            continue
        except Exception, e:
            print "Something failed: ", e

    print "tweets extracted....", len(allTweets)
    return allTweets




# ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **  ~~ **

if __name__ == "__main__":

    if len(sys.argv) > 1:

        key = "XXXX"
        secret = "XXXX"

        access_token = "XXXX"
        access_token_secret = "XXXX"

        # authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(key, secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        screen_name = 'triplejplays'

        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # ternary lols.

        db = accessDB.accessDatabase()

        # ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ #

        if str(sys.argv[1]) == "GET_ALL":
            parsedTweets = get_tweets(api, screen_name, limit=limit)

        # ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ #
        elif str(sys.argv[1]) == "GET_NEW":

            try:
                queryOut = dbQueries.getNewestEntryInDB(db)
                newestID = dbQueries.getEntryforRow(queryOut, 'id')
                print 'newest id was:', newestID, '\n'
                print queryOut, '\n************************\n'

                parsedTweets = get_tweets_after(api, screen_name, since_id=newestID, limit=limit)
            except Exception, e:
                print "Couldn't get newer tweets (perhaps the db is empty? Or you're up to date!)"
                print e
                pass
            # ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ #
        elif str(sys.argv[1]) == "GET_OLD":
            try:
                queryOut = dbQueries.getOldestEntryInDB(db)
                oldestID = dbQueries.getEntryforRow(queryOut, 'id')
                print 'oldest id was:', oldestID, '\n'
                print queryOut, '\n************************\n'


                parsedTweets = get_tweets_before(api, screen_name, max_id=oldestID)
                #parsedTweets = get_tweets_before(api, screen_name, max_id=oldestID, limit=limit)

            except Exception, e:
                print "Couldn't get older tweets (perhaps the db is empty? Or you've got the very first one!...)"
                print e
                pass
        elif str(sys.argv[1]) == "NEWEST_ENTRY":
            try:
                queryOut = dbQueries.getNewestEntryInDB(db)                            
                print queryOut, '\n************************\n'
            except Exception, e:
                print "Couldn't get older tweets (perhaps the db is empty? Or you've got the very first one!...)"
                print e                
            # ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ #
        else:
            print "Your arguments were not recognised:\n"
            for arg in sys.argv:
                print arg

            # ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^  #
        try:
            dbInserts.batchInsert(db, parsedTweets)
        except Exception, e:
            print "\n *** BIG ERROR - your tweets were not inserted into the database *** \n"
            print e

        accessDB.closeConnection(db)

    else:
        print("Please provide some arguments hey")
