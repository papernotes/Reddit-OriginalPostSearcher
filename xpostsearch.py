import praw
import time
import ignoredSubs

r = praw.Reddit(user_agent="XPostOriginalLinker 1.0.0")
r.login(disable_warning=True)

# a list of words that might be an "xpost"
xPostDictionary = ['xpost', 'x post', 'x-post', 'crosspost', 'cross post',
                   'cross-post']
# list of words to check for so we don't post if source is already there
originalComments = ['[source]', '[original]']

# don't bother these subs
ignoredSubs = ignoredSubs.list

xPostTitle = ''     # the xpost title
subLink = None      # the submission shared link
originalSubmission = None   # the originalSubmission
foundLink = False           # boolean if we found a link
cache = []          # the searched posts


# the main driver of the bot
def run_bot():
    global subLink
    global originalSubmission
    global foundLink

    # set up the searched posts cache so we don't recomment, load it
    with open("searchedPosts.txt") as searchedPosts:
        # set up the cache
        cache = searchedPosts.readlines()
        # strip the newlines
        cache = [line.strip('\n') for line in cache]

    # go into the all subreddit
    subreddit = r.get_subreddit("all")

    # get new submissions and see if their titles contain an xpost
    for submission in subreddit.get_new(limit = 25):
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
                        for string in originalComments) or
                        str(comment).find(getOriginalSub(post_title)) != -1):
                    res = False
                    break

            # if we can find the original post
            if res is not False:
                # the original subreddit will contain the original post
                origSub = r.get_subreddit(res)
                # search the original subreddit
                searchOriginalSub(origSub)

                if (foundLink):
                    # comment
                    createCommentString(originalSubmission)

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
            # if we can't fit any of the cases
            else:
                return False
    except:
        print ('failed')
        return False


# Once the title has been found, search the subreddit
def searchOriginalSub(subreddit):
    # accessing the global
    global xPostTitle
    global subLink
    global originalSubmission
    global foundLink

    # if there is an xPostTitle, look for it
    if xPostTitle is not False:
        # for each of the submissions in the subreddit, search the titles
        for submission in subreddit.get_hot(limit = 100):
            # check to see if the string is in the title
            if xPostTitle in submission.title.lower():
                containsTitle = True
            else:
                containsTitle = False

            # if it does contain the title or url, save that submission
            # if (containsTitle or (str(subLink) == str(submission.url))):
            if (containsTitle or
                    (str(subLink) == submission.url.encode('utf-8'))):
                originalSubmission = submission
                foundLink = True
                return
            # If we can't find the original post
            else:
                foundLink = False


# Reply with a comment to the original post
def createCommentString(submissionID):
    string = "XPost from /r/" + str(submissionID.subreddit.display_name) + ":\n" + "[" + str(submissionID.title) + "]" + "(" + submissionID.short_link + ")"
    print string
    print ('\n')
    # add the comment to the submissino
    submissionID.add_comment(string)


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


# Write to the file
def writeToFile(submissionID):
    # set up localCache
    with open("searchedPosts.txt", "r") as searchedPosts:
        localCache = searchedPosts.readlines()
        localCache = [line.strip('\n') for line in localCache]

    # write to file so we don't recomment the posts
    if (submissionID not in localCache):
        with open("searchedPosts.txt", "a") as searchedPosts:
            searchedPosts.write(submissionID)
            searchedPosts.write('\n')


# continuously run the bot
while(True):
    # run the bulk of the bot
    run_bot()

    # start a search again in a couple of minutes (in seconds)
    time.sleep(5)
