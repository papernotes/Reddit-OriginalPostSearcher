""" OriginalPostSearcher bot """
import praw
import time
import ignoredSubs
import nopart
import herokuDB
from sqlalchemy import create_engine
from sqlalchemy import text

REDDIT_CLIENT = praw.Reddit(user_agent="OriginalPostSearcher 1.1.7")
REDDIT_CLIENT.login(disable_warning=True)

# a list of words that might be an "xpost"
X_POST_DICTIONARY = ['xpost', 'x post', 'x-post', 'crosspost', 'cross post',
                     'cross-post', "xposted", "crossposted", "x-posted"]

# list of words to check for so we don't post if source is already there
ORIGINAL_COMMENTS = ['source', 'original', 'original post', 'sauce', 'link',
                     'x-post', 'xpost', 'x-post', 'crosspost', 'cross post',
                     'cross-post', 'referenced']

# create the ENGINE for the database
ENGINE = create_engine(herokuDB.url)

# don't bother these subs
IGNORED_SUBS = ignoredSubs.list

# No participation link subs
NO_PARTICIPATION = nopart.list

X_POST_TITLE = ''        # the xpost title
ORIGINAL_POST = ''       # the original submission
ORIGINAL_LINK = ''       # the original submission link
ORIGINAL_SUBREDDIT = ''  # the original submission's subreddit
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

    # get only new xposts
    xpost_submissions = get_new_xposts(X_POST_DICTIONARY)

    # search for the xpost_submissions
    for submission in xpost_submissions:
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
                print("Res is None - Other Format/Accented/Special Chars")
                res = False

            # if we can find the original post
            if res:
                # the original subreddit will contain the original post
                orig_sub = REDDIT_CLIENT.get_subreddit(res)

                # check to see if there are any "sourced" comments already
                # check to see if original subreddit is mentioned in comments
                print ("Checking comments")

                for comment in submission.comments:
                    if (any(string in str(comment)
                            for string in ORIGINAL_COMMENTS)):
                        print("Source in comments found: ")
                        print(str(comment) + "\n")
                        res = False
                        break

                # if we can find the original submission, comment
                if res and (search_user_posts(submission.author.name, 
                            res, submission.id) or
                            search_duplicates(submission, res) or
                            search_original_sub(orig_sub)):
                    try:
                        print ("Attempting to comment")
                        create_comment_string(submission)
                        res = False
                    except:
                        print ("Commenting failed")
                        res = False

            # if we can't find the original post
            else:
                print ("No res")
                write_to_file(submission.id)

        # save submission to not recomment
        else:
            write_to_file(submission.id)


def get_new_xposts(xpost_dict):
    """
        Searches to get new and most recent xposts
    """
    print "Getting new xposts"

    # Append to a list that will be returned
    xpost_list = []

    # For each string in the xpost dictionary, search for new
    for entry in xpost_dict:

        xpost_titles = REDDIT_CLIENT.search(entry, sort="new")

        # For each search, append those items into the xpost_list
        for item in xpost_titles:
            xpost_list.append(item)

    return xpost_list


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
    global ORIGINAL_SUBREDDIT
    global AUTHOR

    print("Searching other discussions")

    # go into the other discussions tab
    duplicates = sub.get_duplicates(limit=50)

    # check to see if the content contains our subreddit
    for item in duplicates:
        print ("Item is " + str(item))
        # check if the url and subreddit is the same
        if (SUB_LINK.encode('utf-8') == str(item.url).encode('utf-8') and
                item.subreddit.display_name.lower().encode('utf-8') == result):
            print ("Found post in other discussions")
            print ("Title of duplicate: " + item.title.encode('utf-8'))
            ORIGINAL_POST = item.title.encode('utf-8')
            ORIGINAL_LINK = item.permalink
            ORIGINAL_SUBREDDIT = str(item.subreddit)
            AUTHOR = item.author
            return True
        else:
            print("Can't find in other discussions")
            return False

    print ("No other discussions")
    return False


def search_user_posts(poster_name, result, sub_id):
    """
        Checks user's previous posts
    """

    global SUB_LINK
    global ORIGINAL_POST
    global ORIGINAL_LINK
    global ORIGINAL_SUBREDDIT
    global AUTHOR

    print ("Searching user's previous posts")

    # properly get the redditor's posts
    poster_name = poster_name.encode('utf-8')
    poster = REDDIT_CLIENT.get_redditor(poster_name)

    # get the submissions and search
    submissions = poster.get_submitted(limit=100)

    for submission in submissions:
        # Check to see if the link is the same
        if (SUB_LINK.encode('utf-8') == str(submission.url).encode('utf-8') and
            submission.id != sub_id):
            print ("Found post in user's previous posts")
            print ("Title of post: " + str(submission.title).encode('utf-8'))
            ORIGINAL_POST = submission.title.encode('utf-8')
            ORIGINAL_LINK = submission.permalink
            ORIGINAL_SUBREDDIT = str(submission.subreddit)
            AUTHOR = submission.author
            return True
        else:
            print ("Can't find in previous posts")
            return False

    print ("Can't find in previous posts")
    return False


def search_original_sub(original_sub):
    """
        Searches original subreddit after found title
    """

    global X_POST_TITLE
    global SUB_LINK
    global ORIGINAL_POST
    global ORIGINAL_LINK
    global ORIGINAL_SUBREDDIT
    global AUTHOR

    print("Searching original subreddit...")

    # Test to confirm getting subreddit
    try:
        test = original_sub.get_hot(limit=1)
        for submission in test:
            print ("testing: " + str(submission))
    except:
        print("Cannot get subreddit")
        return False

    if X_POST_TITLE:
        # for each of the submissions in the 'hot' subreddit, search
        print("Searching 'Hot'")
        for submission in original_sub.get_hot(limit=200):

            # check to see if the shared content is the same first
            if (SUB_LINK.encode('utf-8') == submission.url.encode('utf-8')):
                ORIGINAL_POST = submission.title.encode('utf-8')
                ORIGINAL_LINK = submission.permalink
                ORIGINAL_SUBREDDIT = str(submission.subreddit)
                AUTHOR = submission.author
                print ("Shared content is the same")
                return True
            else:
                # check to see if the string is in the title
                try:
                    if X_POST_TITLE == submission.title.lower():
                        ORIGINAL_POST = submission.title.encode('utf-8')
                        ORIGINAL_LINK = submission.permalink
                        ORIGINAL_SUBREDDIT = str(submission.subreddit)
                        AUTHOR = submission.author
                        print ("XPost Title is the same")
                        return True
                except:
                    pass

        print("Searching 'New'")
        # if we can't find the cross post in get_hot
        for submission in original_sub.get_new(limit=200):
            # check to see if the shared content is the same first
            if (SUB_LINK.encode('utf-8') == submission.url.encode('utf-8')):
                ORIGINAL_POST = submission.title.encode('utf-8')
                ORIGINAL_LINK = submission.permalink
                ORIGINAL_SUBREDDIT = str(submission.subreddit)
                AUTHOR = submission.author
                print ("Shared content is the same")
                return True
            else:
                # check to see if the string is in the title
                try:
                    if X_POST_TITLE == submission.title.lower():
                        ORIGINAL_POST = submission.title.encode('utf-8')
                        ORIGINAL_LINK = submission.permalink
                        ORIGINAL_SUBREDDIT = str(submission.subreddit)
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


def create_comment_string(sub):
    """
        Reply with a comment to the XPost
    """

    print ("Developing comment")

    global X_POST_TITLE
    global ORIGINAL_POST
    global ORIGINAL_LINK
    global ORIGINAL_SUBREDDIT
    global AUTHOR

    # set the original_sub fix
    original_sub = get_original_sub(sub.title)
    # None fix
    if original_sub == 'None':
        return
    # Author fix
    if not AUTHOR:
        AUTHOR = "a [deleted] user"
    else:
        AUTHOR = "/u/" + str(AUTHOR)


    # no participation link
    if (sub.subreddit.display_name.lower() in NO_PARTICIPATION and
            "www.reddit.com/r/" in ORIGINAL_LINK):
        print ("Using No Participation link")
        original_link_list = ORIGINAL_LINK.split("https://www.")
        ORIGINAL_LINK = "http://np." + original_link_list[1]

    # Create the string to comment with
    comment_string = ("X-Post referenced from /r/" +
                      ORIGINAL_SUBREDDIT + " by " + AUTHOR +
                      "  \n[" + ORIGINAL_POST.encode('utf-8') +
                      "](" + ORIGINAL_LINK.encode('utf-8') +
                      ")\n*****  \n  \n^^I ^^am ^^a ^^bot ^^made ^^for "
                      "^^your ^^convenience ^^\(Especially ^^for " +
                      "^^mobile ^^users).  \n^^[Contact]" +
                      "(https://www.reddit.com/message/" +
                      "compose/?to=OriginalPostSearcher)" +
                      " ^^| ^^[Code](https://github.com/" +
                      "papernotes/Reddit-OriginalPostSearcher)")

    print comment_string

    # add the comment to the submission
    sub.add_comment(comment_string)

    # upvote for proper camaraderie
    sub.upvote()
    print("\nCommented!")


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


def clear_database():
    """
        Clear our column/database if our rowcount is too high
        Also cuts the CACHE in half
    """

    global CACHE

    num_rows = ENGINE.execute("select * from searched_posts")
    if (num_rows.rowcount > 2000):
        ENGINE.execute("delete from searched_posts")
        print("Cleared database")

    if len(CACHE) > 2000:
        # Cut CACHE in half, keep last half
        CACHE = CACHE[int(len(CACHE))/2:]
        print ("Halved CACHE")


print ("Starting bot")

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
    time.sleep(10)

    # clear the column to stay in compliance
    clear_database()
