import os
import psycopg2
import praw
import time
import ignoredSubs
import herokuDB
from sqlalchemy import create_engine
from sqlalchemy import text

r = praw.Reddit(user_agent="XPostOriginalLinker 1.0.0")
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
subLink = None      # the submission shared link
foundLink = False   # boolean if we found a link
cache = []          # the searched posts
tempCache = []


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
    for submission in subreddit.get_new(limit = 100):
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
            print ("XPost found!")
            print ("post title = " + post_title)
            subLink = submission.url
            print ("shared link = " + subLink + '\n')

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

                if (foundLink):
                    # comment
                    createCommentString(submission)

            # if we can't find the original post
            else:
                writeToFile(submission.id)

        # save submission to not recomment
        else:
            writeToFile(submission.id)


# Find the original subreddit of the original submission
# Returns the title of the original subreddit
def getOriginalSub(title):
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
                return word
            elif 'r/' in word:
                # split for r/
                word = word.split('r/')[1]
                word = word.split(')')[0]   # try for parentheses first
                word = word.split(']')[0]   # try for brackets
                return word
    except:
        print ('failed')
        return False


# Once the title has been found, search the subreddit
def searchOriginalSub(subreddit):
    # accessing the global
    global xPostTitle
    global subLink
    global foundLink
    global originalPost
    global originalLink

    # if there is an xPostTitle, look for it
    if xPostTitle is not False:
        # for each of the submissions in the subreddit, search the titles
        for submission in subreddit.get_hot(limit = 150):
            try:
                # check to see if the string is in the title
                if xPostTitle in submission.title.lower():
                    containsTitle = True
                else:
                    containsTitle = False
            except:
                pass

            # if it does contain the title or url, save that submission
            # if (containsTitle or (str(subLink) == str(submission.url))):
            if (containsTitle or
                    (str(subLink) == submission.url.encode('utf-8'))):
                foundLink = True
                originalPost = submission.title.encode('utf-8')
                originalLink = submission.short_link
                return
            # If we can't find the original post
            else:
                foundLink = False


# Reply with a comment to the original post
def createCommentString(submissionID):
    global xPostTitle
    global originalPost
    global originalLink
    
    originalSub = getOriginalSub(submissionID.title)
    # none fix
    if originalSub == 'None':
        return
        string = "XPost from /r/" + str(getOriginalSub(submissionID.title)) + ":  \n[" + str(originalPost) + "](" + str(originalLink) + ")  \n  \n^^I ^^am ^^a ^^bot, ^^PM ^^me ^^if ^^you ^^have ^^any ^^questions"
    print string
    print ('\n')
    # add the comment to the submission
    submissionID.add_comment(string)
    # upvote for proper camaraderie
    submissionID.upvote()


# gets the title of the post to compare/see if
#   original has the same title
# Returns the title of the xpost
def getTitle(title):
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
    if (numRows.rowcount > 9000):
        engine.execute("delete from searched_posts")
        print ("Cleared")

# continuously run the bot
while(True):
    # run the bulk of the bot
    run_bot()

    # reset the cache
    tempCache = []

    # start a search again in a couple of minutes (in seconds)
    time.sleep(300)

    # clear the column to stay in compliance
    clearColumn()
