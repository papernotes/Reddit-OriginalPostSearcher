""" OriginalPostSearcher bot """
import praw
import time
import ignoredSubs
import herokuDB
from sqlalchemy import create_engine
from sqlalchemy import text

REDDIT_CLIENT = praw.Reddit(user_agent="OriginalPostSearcher 1.1.3")
REDDIT_CLIENT.login(disable_warning=True)

# a list of words that might be an "xpost"
X_POST_DICTIONARY = ['xpost', 'x post', 'x-post', 'crosspost', 'cross post',
                     'cross-post']
# list of words to check for so we don't post if source is already there
ORIGINAL_COMMENTS = ['source', 'original', 'original post', 'sauce', 'link']

# create the ENGINE for the database
ENGINE = create_engine(herokuDB.url)

# don't bother these subs
IGNORED_SUBS = ignoredSubs.list

X_POST_TITLE = ''        # the xpost title
ORIGINAL_POST = ''       # the original submission
ORIGINAL_LINK = ''       # the original submission link
SUB_LINK = None          # the submission shared link
CACHE = []               # the searched posts
TEMP_CACHE = []          # temporary CACHE to get from database
AUTHOR = ''              # the author of the submission


def run_bot():
    """
        Main driver of the bot
    """

    global SUB_LINK
    global CACHE

    # set up the searched posts CACHE so we don't recomment
    # get the values in the table
    result = ENGINE.execute("select * from searched_posts")

    # set up the TEMP_CACHE
    for row in result:
        TEMP_CACHE.append(str(row[0]))

    # set up the CACHE
    for value in TEMP_CACHE:
        if value not in CACHE:
            CACHE.append(str(value))

    # go into the all subreddit
    subreddit = REDDIT_CLIENT.get_subreddit("all")

    # get new submissions and see if their titles contain an xpost
    for submission in subreddit.get_new(limit=200):
        # make sure we don't go into certain subreddits
        if (submission.subreddit.display_name.lower() in IGNORED_SUBS or
                submission.over_18 is True):
            write_to_file(submission.id)
            continue
        # save the submission's title
        post_title = submission.title.lower()

        # change into utf-8
        try:
            post_title = post_title.encode('utf-8')
        except:
            pass

        # if the submission title is in the X_POST_DICTIONARY, find original
        if (any(string in post_title for string in X_POST_DICTIONARY) and
                submission.id not in CACHE):
            print("\nXPost found!")
            print("subreddit = " + str(submission.subreddit.display_name.lower()))
            print("post title = " + post_title)

            # set the SUB_LINK
            SUB_LINK = submission.url

            # save submission to not recomment
            write_to_file(submission.id)

            # get the original subreddit title
            res = get_original_sub(post_title)

            # to fix NoneType error, for accented/special chars
            if res is None:
                print("Res is None - Accented/Special Chars")
                res = False

            # if we can find the original post
            if res:
                # the original subreddit will contain the original post
                orig_sub = REDDIT_CLIENT.get_subreddit(res)

                # check to see if there are any "sourced" comments already
                # check to see if original subreddit is mentioned in comments
                for comment in submission.comments:
                    if (any(string in str(comment)
                            for string in ORIGINAL_COMMENTS) or
                            str(comment).find(res) == -1):
                        print("Source in comments found: ")
                        print(str(comment) + "\n")
                        res = False
                        break

                # if we can find the original submission, comment
                if res is not False and (search_duplicates(submission, res) or
                                         search_original_sub(orig_sub)):
                    try:
                        create_comment_string(submission)
                        res = False
                    except:
                        res = False

            # if we can't find the original post
            else:
                write_to_file(submission.id)

        # save submission to not recomment
        else:
            write_to_file(submission.id)


def get_original_sub(title):
    """
        Returns title of original subreddit
    """

    print("Getting original subreddit of: " + str(title))
    global X_POST_TITLE

    X_POST_TITLE = get_title(title)

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
                print("/r/ word = " + word.encode('utf-8'))
                return word
            elif 'r/' in word:
                # split for r/
                word = word.split('r/')[1]
                word = word.split(')')[0]   # try for parentheses first
                word = word.split(']')[0]   # try for brackets
                print("r/ word = " + word.encode('utf-8'))
                return word
    except:
        print("Could not get original subreddit")
        return False


def search_duplicates(sub, result):
    """
        Search the duplicates/other discussions to save time
    """

    global SUB_LINK
    global ORIGINAL_POST
    global ORIGINAL_LINK
    global AUTHOR

    print("Searching other discussions")

    # go into the other discussions tab
    duplicates = sub.get_duplicates()

    # check to see if the content contains our subreddit
    for item in duplicates:
        # check if the url and subreddit is the same
        if (SUB_LINK.encode('utf-8') == str(item.url).encode('utf-8') and
                item.subreddit.display_name.lower().encode('utf-8') == result):
            print ("Found post in other discussions")
            ORIGINAL_POST = item.title.encode('utf-8')
            ORIGINAL_LINK = item.permalink
            AUTHOR = item.author
            return True
        else:
            print("Can't find in other discussions")
            return False

    print ("No other discussions")
    return False


def search_original_sub(originalSubreddit):
    """
        Searches original subreddit after found title
    """

    global X_POST_TITLE
    global SUB_LINK
    global ORIGINAL_POST
    global ORIGINAL_LINK
    global AUTHOR

    print("Searching original subreddit...")

    # Test to confirm getting subreddit
    try:
        test = originalSubreddit.get_hot(limit=1)
        for submission in test:
            print ("testing: " + str(submission))
    except:
        print("Cannot get subreddit")
        return False

    if X_POST_TITLE:
        # for each of the submissions in the 'hot' subreddit, search
        print("Searching 'Hot'")
        for submission in originalSubreddit.get_hot(limit=250):

            # check to see if the shared content is the same first
            if (SUB_LINK.encode('utf-8') == submission.url.encode('utf-8')):
                ORIGINAL_POST = submission.title.encode('utf-8')
                ORIGINAL_LINK = submission.permalink
                AUTHOR = submission.author
                print ("Shared content is the same")
                return True
            else:
                # check to see if the string is in the title
                try:
                    if X_POST_TITLE == submission.title.lower():
                        ORIGINAL_POST = submission.title.encode('utf-8')
                        ORIGINAL_LINK = submission.permalink
                        AUTHOR = submission.author
                        print ("XPost Title is the same")
                        return True
                except:
                    pass

        print("Searching 'New'")
        # if we can't find the cross post in get_hot
        for submission in originalSubreddit.get_new(limit=100):
            # check to see if the shared content is the same first
            if (SUB_LINK.encode('utf-8') == submission.url.encode('utf-8')):
                ORIGINAL_POST = submission.title.encode('utf-8')
                ORIGINAL_LINK = submission.permalink
                AUTHOR = submission.author
                print ("Shared content is the same")
                return True
            else:
                # check to see if the string is in the title
                try:
                    if X_POST_TITLE == submission.title.lower():
                        ORIGINAL_POST = submission.title.encode('utf-8')
                        ORIGINAL_LINK = submission.permalink
                        AUTHOR = submission.author
                        print ("XPost Title is the same")
                        return True
                except:
                    pass
        # if we can't find the original post
        print("Could not find original post - Hot/New Search Failed")
        return False
    else:
        print("Could not find original post - No X_POST_TITLE")
        return False


def create_comment_string(sub_id):
    """
        Reply with a comment to the XPost
    """

    global X_POST_TITLE
    global ORIGINAL_POST
    global ORIGINAL_LINK
    global AUTHOR

    # set the original_sub fix
    original_sub = get_original_sub(sub_id.title)
    # None fix
    if original_sub == 'None':
        return
    # Author fix
    if not AUTHOR:
        AUTHOR = "a [deleted] user"
    else:
        AUTHOR = "/u/" + str(AUTHOR)
    # Create the string to comment with
    comment_string = ("Original Post referenced from /r/" +
                      get_original_sub(sub_id.title).encode('utf-8') +
                      " by " + AUTHOR +
                      "  \n[" + ORIGINAL_POST.encode('utf-8') +
                      "](" + ORIGINAL_LINK.encode('utf-8') +
                      ")\n*****  \n  \n^^I ^^am ^^a ^^bot ^^made ^^for "
                      "^^your ^^convenience ^^\(Especially ^^for ^^mobile ^^users)"
                      ".  \n^^PM ^^me ^^if "
                      "^^you ^^have ^^any ^^questions ^^or ^^suggestions.")

    print("\nCommented!")
    print comment_string

    # add the comment to the submission
    sub_id.add_comment(comment_string)
    # upvote for proper camaraderie
    sub_id.upvote()


def get_title(title):
    """
        Gets the title of the XPost for comparison
    """
    print("Getting the title of: " + str(title))
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
        print ("Couldn't get title correctly")
        return None


def delete_negative():
    """
        Delete badly received comments
    """
    user = REDDIT_CLIENT.get_redditor('OriginalPostSearcher')
    submitted = user.get_comments(limit=200)
    for item in submitted:
        if int(item.score) < 0:
            print("\nDeleted negative comment\n        " + str(item))
            item.delete()


# Database

def write_to_file(sub_id):
    """
        Save the submissions we searched
    """

    if not id_added(sub_id):
        temp_text = text('insert into searched_posts (post_id) values(:postID)')
        ENGINE.execute(temp_text, postID=sub_id)


def id_added(sub_id):
    """
        Check to see if the item is already in the database
    """

    is_added_text = text("select * from searched_posts where post_id = :postID")
    return ENGINE.execute(is_added_text, postID=sub_id).rowcount != 0


def clear_column():
    """
        Clear our column/database if our rowcount is too high
    """

    num_rows = ENGINE.execute("select * from searched_posts")
    if (num_rows.rowcount > 2000):
        ENGINE.execute("delete from searched_posts")
        print("Cleared database")


# continuously run the bot
while True:
    # run the bulk of the bot
    run_bot()

    # reset the CACHE
    TEMP_CACHE = []

    # delete unwanted posts if there are any
    delete_negative()

    # start a search again after a while
    print("Sleeping...")
    time.sleep(15)

    # clear the column to stay in compliance
    clear_column()
