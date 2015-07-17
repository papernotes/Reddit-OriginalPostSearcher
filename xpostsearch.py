import praw
import time
import ignoredSubs
import herokuDB
from sqlalchemy import create_engine
from sqlalchemy import text

r = praw.Reddit(user_agent="XPostOriginalLinker 1.0.3")
r.login(disable_warning=True)

# a list of words that might be an "xpost"
xPostDictionary = ['xpost', 'x post', 'x-post', 'crosspost', 'cross post',
                   'cross-post']
# list of words to check for so we don't post if source is already there
originalComments = ['source', 'original']

# create the engine for the database
engine = create_engine(herokuDB.url)

# don't bother these subs
ignoredSubs = ignoredSubs.list

xPostTitle = ''     # the xpost title
originalPost = ''   # the original submission
originalLink = ''   # the original submission link
containsTitle = False   # boolean if we have the title
subLink = None      # the submission shared link
foundLink = False   # boolean if we found a link
cache = []          # the searched posts
tempCache = []      # temporary cache to get from database


# the main driver of the bot
def run_bot():
    global subLink
    global foundLink
    global cache

    # set up the searched posts cache so we don't recomment
    # get the values in the table
    result = engine.execute("select * from searched_posts")

    # set up the tempCache
    for row in result:
        tempCache.append(str(row[0]))

    # set up the cache
    for value in tempCache:
        if value not in cache:
            cache.append(str(value))

    # go into the all subreddit
    subreddit = r.get_subreddit("all")

    # get new submissions and see if their titles contain an xpost
    for submission in subreddit.get_new(limit = 200):
        # make sure we don't go into certain subreddits
        if (submission.subreddit.display_name.lower() in ignoredSubs or
                submission.over_18 is True):
            writeToFile(submission.id)
            continue
        # save the submission's title
        post_title = submission.title.lower()

        # change into utf-8
        try:
            post_title = post_title.encode('utf-8')
        except:
            pass

        # if the submission title is in the xPostDictionary, find original
        if (any(string in post_title for string in xPostDictionary) and
                submission.id not in cache):
            print ("\nXPost found!")
            print ("subreddit = " + str(submission.subreddit.display_name.lower()))
            print ("post title = " + post_title)

            # set the subLink
            subLink = submission.url

            # save submission to not recomment
            writeToFile(submission.id)

            # get the original subreddit title
            res = getOriginalSub(post_title)

            # check to see if there are any "sourced" comments already
            # check to see if original subreddit is mentioned in comments
            for comment in submission.comments:
                if (any(string in str(comment)
                        for string in originalComments)):
                    res = False
                    break

            # to fix NoneType error
            if res is None:
                res = False

            # if we can find the original post
            if res is not False:
                # the original subreddit will contain the original post
                origSub = r.get_subreddit(res)
                # search the original subreddit
                searchOriginalSub(origSub)

                if foundLink:
                    # comment
                    try:
                        createCommentString(submission)
                        res = False
                        foundLink = False
                    except:
                        res = False
                        foundLink = False
                        pass

            # if we can't find the original post
            else:
                writeToFile(submission.id)

        # save submission to not recomment
        else:
            writeToFile(submission.id)


# Find the original subreddit of the original submission
# Returns the title of the original subreddit
def getOriginalSub(title):
    print ("Getting original subreddit of: " + str(title))
    # accesing the global xPostTitle
    global xPostTitle
    # set the xPostTitle
    xPostTitle = getTitle(title)

    # Attempt to find the first /r/ phrase/subreddit
    try:
        # split the title into a list of words
        title = title.split()

        # for each element in that title, look for '/r/'
        for word in title:
            # if it's found, strip the '/r/' and return the subreddit
            if '/r/' in word:
                # split from /r/
                word = word.split('/r/')[1]
                word = word.split(')')[0]   # try for parentheses first
                word = word.split(']')[0]   # try for brackets
                print ("/r/ word = " + word.encode('utf-8'))
                return word
            elif 'r/' in word:
                # split for r/
                word = word.split('r/')[1]
                word = word.split(')')[0]   # try for parentheses first
                word = word.split(']')[0]   # try for brackets
                print ("r/ word = " + word.encode('utf-8'))
                return word
    except:
        print ("Could not get original subreddit")
        return False


# Once the title has been found, search the subreddit
def searchOriginalSub(subreddit):
    # accessing the global
    global xPostTitle
    global subLink
    global foundLink
    global originalPost
    global originalLink
    global containsTitle

    print ("Searching original subreddit...")

    if xPostTitle is not False:
        # for each of the submissions in the 'hot' subreddit, search
        print ("Searching 'Hot'")
        for submission in subreddit.get_hot(limit = 250):

            # check to see if the shared content is the same first
            if (subLink.encode('utf-8') == submission.url.encode('utf-8')):
                foundLink = True
                originalPost = submission.title.encode('utf-8')
                originalLink = submission.permalink
                return
            else:
                # check to see if the string is in the title
                try:
                    if xPostTitle in submission.title.lower():
                        foundLink = True
                        originalPost = submission.title.encode('utf-8')
                        originalLink = submission.permalink
                        return
                except:
                    pass

        print ("Searching 'New'")
        # if we can't find the cross post in get_hot
        for submission in subreddit.get_new(limit = 50):
            # check to see if the shared content is the same first
            if (subLink.encode('utf-8') == submission.url.encode('utf-8')):
                foundLink = True
                originalPost = submission.title.encode('utf-8')
                originalLink = submission.permalink
                return
            else:
                # check to see if the string is in the title
                try:
                    if xPostTitle in submission.title.lower():
                        foundLink = True
                        originalPost = submission.title.encode('utf-8')
                        originalLink = submission.permalink
                        return
                except:
                    pass
        # if we can't find the original post
        foundLink = False


# Reply with a comment to the original post
def createCommentString(submissionID):
    global xPostTitle
    global originalPost
    global originalLink

    # set the originalSub fix
    originalSub = getOriginalSub(submissionID.title)
    # None fix
    if originalSub == 'None':
        return
    # Create the string to comment with
    commentString = ("XPost from /r/" +
                     getOriginalSub(submissionID.title).encode('utf-8') +
                     ":  \n[" + originalPost.encode('utf-8') +
                     "](" + originalLink.encode('utf-8') +
                     ")  \n  \n^^I ^^am ^^a ^^bot, ^^PM ^^me ^^if "
                     "^^you ^^have ^^any ^^questions ^^or ^^suggestions")

    print ("Commented!")
    print commentString

    # add the comment to the submission
    submissionID.add_comment(commentString)
    # upvote for proper camaraderie
    submissionID.upvote()


# gets the title of the post to compare/see if
#   original has the same title
# Returns the title of the xpost
def getTitle(title):
    print ("Getting the title of: " + str(title))
    # format TITLE(xpost)
    if (len(title) == title.find(')') + 1):
        return title.split('(')[0]
    # format TITLE[xpost]
    elif (len(title) == title.find(']') + 1):
        return title.split('[')[0]
    # format (xpost)TITLE
    elif (title.find('(') == 0):
        return title.split(')')[1]
    # format [xpost]TITLE
    elif (title.find('[') == 0):
        return title.split('[')[1]
    # weird format, return false
    else:
        return False


# delete badly received comments
def deleteNegative():
    user = r.get_redditor('OriginalPostSearcher')
    submitted = user.get_comments(limit = 50)
    for item in submitted:
        if int(item.score) < 0:
            print ("\nDeleted negative comment\n        " + str(item))
            item.delete()


# DATABASE
# Write to the file
def writeToFile(submissionID):
    if isAdded(submissionID) is False:
        tempText = text('insert into searched_posts (post_id) values(:postID)')
        engine.execute(tempText, postID = submissionID)


# Check if we're added to the database
def isAdded(submissionID):
    isAddedText = text("select * from searched_posts where post_id = :postID")
    if (engine.execute(isAddedText, postID = submissionID).rowcount != 0):
        return True
    else:
        return False


# Clear out the column if our rowcount too high
def clearColumn():
    numRows = engine.execute("select * from searched_posts")
    if (numRows.rowcount > 1500):
        engine.execute("delete from searched_posts")
        print ("Cleared database")


# continuously run the bot
while True:
    # run the bulk of the bot
    run_bot()

    # reset the cache
    tempCache = []

    # delete unwanted posts if there are any
    deleteNegative()

    # start a search again in one minute
    print ("Sleeping...")
    time.sleep(60)

    # clear the column to stay in compliance
    clearColumn()
