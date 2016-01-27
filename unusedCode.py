
# def get_last_n_tweets(api, screen_name, nTweets):
#     # Twitter only allows access to a users most recent 3240 tweets with this method
#
#     if nTweets < 3200:
#         return api.user_timeline(screen_name=screen_name, count=nTweets)


# def get_all_tweets(api, screen_name, max_depth=-1):
#     # Twitter only allows access to a users most recent 3240 tweets with this method
#
#     # initialize a list to hold all the tweepy Tweets
#     alltweets = []
#
#     # set some kind of count here
#     nTweetsPerRequest = 200
#
#     # make initial request for most recent tweets (200 is the maximum allowed count)
#     new_tweets = api.user_timeline(screen_name=screen_name, count=nTweetsPerRequest)
#
#     # save most recent tweets
#     alltweets.extend(new_tweets)
#
#     # save the id of the oldest tweet less one
#     oldest = alltweets[-1].id - 1
#
#     # keep track of depth in case you dont want to hit Twitter's request limiter
#     nCalls = 0
#
#     # keep grabbing tweets until there are no tweets left to grab
#     while len(new_tweets) > 0:
#         print "getting tweets before id: %s" % (oldest)
#
#         # all subsiquent requests use the max_id param to prevent duplicates
#         new_tweets = api.user_timeline(screen_name=screen_name, count=nTweetsPerRequest, max_id=oldest)
#
#         # save most recent tweets
#         alltweets.extend(new_tweets)
#
#         # update the id of the oldest tweet less one
#         oldest = alltweets[-1].id - 1
#
#         print "...%s tweets downloaded so far" % (len(alltweets))
#
#         # If you've made your max number of calls, leave
#         nCalls += 1
#         if max_depth != -1 and nCalls == max_depth:
#             break
#
#     return alltweets


# def get_past_tweets(api, screen_name, hours=0, days=0, weeks=0, stepSize=20):
#     # no negative values
#     days = abs(days)
#     weeks = abs(weeks)
#
#     earliestPoint = datetime.datetime.now() - datetime.timedelta(hours=hours, days=days,
#                                                                  weeks=weeks)  # SUB IN ARGS LATER
#     print "TIME CUTOFF: " + str(earliestPoint)
#
#     # initialize a list to hold all the tweepy Tweets
#     alltweets = []
#
#     curTime = datetime.datetime.now()
#     stepSize = 3000  # PICK SOMETHING REASONABLE
#     oldestID = -1
#
#     while earliestPoint < curTime:
#
#         # Start at max_id
#         if oldestID == -1:
#             new_tweets = api.user_timeline(screen_name=screen_name, count=stepSize)
#         else:
#             new_tweets = api.user_timeline(screen_name=screen_name, count=stepSize, max_id=oldestID)
#
#         # save most recent tweets, but only those that conform
#         for tweet in new_tweets:
#             # print "Tweet creation time: " + str(tweet.created_at) + "(" + str(tweet.text) + ") VS Crit Time: " + str(earliestPoint) + " >>> " + str(tweet.created_at > earliestPoint)
#             if tweet.created_at > earliestPoint:
#                 alltweets.append(tweet)
#             else:
#                 break  # better than a while loop coz of the iterator
#
#         # Try because what if NO tweets are added to either and thus [-1] is out of bounds.
#         try:
#             """ These variables are used to exit the loop & start where we left off last loop"""
#             oldestID = alltweets[-1].id - 1  # update the id of the oldestID tweet less one
#             curTime = new_tweets[-1].created_at  # The creation time of the last tweet in the list
#         except:
#             pass
#
#     print len(alltweets), "tweets since", earliestPoint
#
#     if len(new_tweets) == 0:
#         return
#
#     return alltweets

def getSongsPlayedBetween(db, startTime, endTime):

    #Strip the microseconds
    startTime = startTime.strftime("%Y-%m-%d %H:%M:%S")
    endTime = endTime.strftime("%Y-%m-%d %H:%M:%S")

    query = "SELECT DISTINCT * FROM `Plays` WHERE `time` > \'" + startTime + "\' AND " + "`time` < \'" + endTime + "\'"
    print query

    cur = db.cursor()
    cur.execute(query)

    return outputQueryFetchall(cur)

def getSongsByArtist(db, twitterhandle):

    query = "SELECT DISTINCT * FROM `Plays` WHERE `artist` = \'" + twitterhandle + "\'"

    cur = db.cursor()
    cur.execute(query)

    return outputQueryFetchall(cur)


def get_all_tweets(api, screen_name, oldest_id=-1):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    if oldest_id != -1:
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest_id)
    else:
        new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    print new_tweets

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print "getting tweets before %s" % (oldest)

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print "...%s tweets downloaded so far" % (len(alltweets))

    # transform the tweepy tweets into a 2D array that will populate the csv

    outtweets = []

    for tweet in alltweets:
        outtweets.append(parseTweet(tweet))

    return outtweets
