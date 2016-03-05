""" OriginalPostSearcher bot """
import herokuDB
import ignoredSubs
import nopart
import praw
import time
from sqlalchemy import create_engine
from sqlalchemy import text

REDDIT_CLIENT = praw.Reddit(user_agent="OriginalPostSearcher 1.2.2")
REDDIT_CLIENT.login(disable_warning=True)

# a list of words that might be an "xpost"

X_POST_DICTIONARY = set()
X_POST_DICTIONARY.update(["xpost", "x-post", "crosspost","cross-post",
                     "xposted", "crossposted", "x-posted"])


# list of words to check for so we don't post if source is already there
ORIGINAL_COMMENTS = set()
ORIGINAL_COMMENTS.update(['source', 'original', 'original post', 'sauce', 'link',
                     'x-post', 'xpost', 'x-post', 'crosspost', 'cross post',
                     'cross-post', 'referenced', 'credit', 'credited', 'other',
                     'post'])

# create the ENGINE for the database
ENGINE = create_engine(herokuDB.url)

# don't bother these subs
IGNORED_SUBS = set()
IGNORED_SUBS.update(ignoredSubs.ignore_list)

# No participation link subs
NO_PARTICIPATION = set()
NO_PARTICIPATION.update(nopart.nopart_list)


class SearchBot(object):
    def __init__(self):
        self.xpost_dict = X_POST_DICTIONARY
        self.engine = ENGINE
        self.ignored_subs = IGNORED_SUBS

        # cache for database
        self.cache = set()
        self.temp_cache = set()
        self.xpost_submissions = set()

        # fields for the xposted submission
        self.xpost_url = None                   # link shared in the submission
        self.xpost_permalink = None
        self.xpost_title = None
        self.xpost_author = None
        self.xpost_sub = None

        # fields for the original subreddit
        self.original_sub = None                # subreddit object
        self.original_sub_title = None          # title of the subreddit
        self.original_title = None
        self.original_permalink = None
        self.original_author = None


    def setup_database_cache(self):
        result = self.engine.execute("select * from searched_posts")

        for row in result:
            self.temp_cache.add(str(row[0]))

        for value in self.temp_cache:
            if value not in self.cache:
                self.cache.add(str(value))


    def set_xpost_submissions(self, search_terms, client):
        """
            Searches for the most recent xposts and sets it
        """
        print "Finding xposts"
        for entry in search_terms:
            for title in client.search(entry, sort="new"):
                self.xpost_submissions.add(title)


    def write_to_file(self, sub_id):
        """
            Saves the submission we just searched
        """
        if not self.id_added(sub_id):
            temp_text = text('insert into searched_posts (post_id) values(:postID)')
            self.engine.execute(temp_text, postID=sub_id)


    def id_added(self, sub_id):
        id_added_text = text("select * from searched_posts where post_id = :postID")
        return self.engine.execute(id_added_text, postID=sub_id).rowcount != 0


    def is_xpost(self, submission):
        submission_title = submission.title.lower()
        try:
            submission_title = submission_title.encode('utf-8')
        except:
            pass
            return False
        return any(string in submission_title for string in self.xpost_dict)


    def get_xpost_title(self, title):
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


    def get_original_sub(self):
        try:
            self.xpost_title = self.xpost_title.split()
        except:
            print "Failed split"
            pass
            self.original_sub_title = None
            return
        try:
            for word in self.xpost_title:
                if '/r/' in word:
                    # split from /r/
                    word = word.split('/r/')[1]
                    word = word.split(')')[0]   # try for parentheses first
                    word = word.split(']')[0]   # try for brackets
                    print("/r/ word = " + word.encode('utf-8'))
                    self.original_sub_title = word
                    break
                # split for "r/" only format
                elif 'r/' in word:
                    word = word.split('r/')[1]
                    word = word.split(')')[0]   # try for parentheses first
                    word = word.split(']')[0]   # try for brackets
                    print("r/ word = " + word.encode('utf-8'))
                    self.original_sub_title = word
                    break
                else:
                    self.original_sub_title = None
        except:
            print("Could not get original subreddit")
            self.original_sub_title = None


    def has_source(self, submission):
        for comment in submission.comments:
            try:
                if (any(string in str(comment.body).lower()
                        for string in ORIGINAL_COMMENTS)):
                    print("Source in comments found: ")
                    print("     " + str(comment.body) + "\n")
                    return True
            except:
                pass

        print "No 'source' comments found"
        return False


    def search_for_post(self, submission, lim):
        duplicates = submission.get_duplicates(limit=lim)

        print "Searching Dupes"
        for submission in duplicates:
            if self.is_original(submission):
                self.original_permalink = submission.permalink
                return True

        poster_name = self.xpost_author.encode('utf-8')
        poster = REDDIT_CLIENT.get_redditor(poster_name)
        user_submissions = poster.get_submitted(limit=lim)

        print "Searching User"
        for submission in user_submissions:
            if self.is_original(submission):
                self.original_permalink = submission.permalink
                return True

        # in case the subreddit doesn't exist
        try:
            self.original_sub = REDDIT_CLIENT.get_subreddit(self.original_sub_title)

            print "Searching New"
            for submission in self.original_sub.get_new(limit=lim):
                if self.is_original(submission):
                    self.original_permalink = submission.permalink
                    return True

            print "Searching Hot"
            for submission in self.original_sub.get_hot(limit=lim):
                if self.is_original(submission):
                    self.original_permalink = submission.permalink
                    return True
        except:
            pass
            return False

        print "--------------Failed all searches"
        return False


    def is_original(self, submission):
        try:
            if (self.xpost_url == str(submission.url).encode('utf-8') and
                submission.subreddit.display_name.lower().encode('utf-8') == self.original_sub_title and
                submission.over_18 is False and
                not self.xpost_permalink in submission.permalink):
                self.set_original_fields(submission)
                return True
            return False
        except:
            pass
            return False


    def reset_fields(self):
        self.original_sub_title = None
        self.original_found = False


    def set_xpost_fields(self, submission):
        try:
            self.xpost_url = submission.url.encode('utf-8')
            self.xpost_permalink = submission.permalink
            self.xpost_author = submission.author.name
            self.xpost_title = submission.title.lower().encode('utf-8')
            self.xpost_sub = submission.subreddit
        except:
            pass


    def set_original_fields(self, submission):
        try:
            self.original_title = submission.title.encode('utf-8')
            self.original_link = submission.permalink
            self.original_author = submission.author
            self.original_found = True
        except:
            pass


    def clear_database(self):
        num_rows = ENGINE.execute("select * from searched_posts")

        if num_rows.rowcount > 1000:
            ENGINE.execute("delete from searched_posts")
            print "Cleared database"
        if len(self.cache) > 1000:
            self.cache = self.cache[int(len(self.cache))/2:]
            print "Halved cache"


    def delete_negative(self):
        print "Checking previous comments for deletion"
        user = REDDIT_CLIENT.get_redditor('OriginalPostSearcher')
        submitted = user.get_comments(limit=150)
        for item in submitted:
            if int(item.score) < -1:
                print("\nDeleted negative comment\n        " + str(item))
                item.delete()


    def create_comment(self, submission):
        print "Making comment\n"
        if not self.original_author:
            self.original_author = "a [deleted] user"
        else:
            self.original_author = "/u/" + str(self.original_author)

        # no participation link
        if (submission.subreddit.display_name.lower() in NO_PARTICIPATION and
            "www.reddit.com/r/" in self.original_link):
            print ("Using No Participation link")
            original_link_list = self.original_link.split("https://www.")
            self.original_link = "http://np." + original_link_list[1]

        # create the string to comment with
        comment_string = ("X-Post referenced from /r/" +
                      self.original_sub_title + " by " + self.original_author +
                      "  \n[" + self.original_title.encode('utf-8') +
                      "](" + self.original_link.encode('utf-8') +
                      ")\n*****  \n  \n^^I ^^am ^^a ^^bot ^^made ^^for "
                      "^^your ^^convenience ^^\(Especially ^^for " +
                      "^^mobile ^^users)." + "  \n^^P.S. ^^negative ^^comments " +
                      "^^get ^^deleted.  \n^^[Contact]" +
                      "(https://www.reddit.com/message/" +
                      "compose/?to=OriginalPostSearcher)" +
                      " ^^| ^^[Code](https://github.com/" +
                      "papernotes/Reddit-OriginalPostSearcher)" +
                      " ^^| ^^[FAQ](https://github.com/papernotes/" +
                      "Reddit-OriginalPostSearcher#faq)")
        print comment_string

        # double check
        if self.has_source(submission):
            print "Source found"
        else:
            submission.add_comment(comment_string)
            print "\nCommented!"


    def is_ignored_nsfw(self, submission):
        return not (submission.subreddit.display_name.lower() in self.ignored_subs or
           submission.over_18 is True)


if __name__ == '__main__':
    bot = SearchBot()
    print "Created bot"

    while True:
        bot.set_xpost_submissions(X_POST_DICTIONARY, REDDIT_CLIENT)
        bot.setup_database_cache()

        for submission in bot.xpost_submissions:
            # NSFW content or ignored subreddit
            if not bot.is_ignored_nsfw(submission) and submission.id not in bot.cache:
                bot.write_to_file(submission.id)
                bot.reset_fields()
                continue

            if bot.is_xpost(submission) and submission.id not in bot.cache:
               
                bot.set_xpost_fields(submission)

                try:
                    if "reddit" in bot.xpost_url.encode('utf-8'):
                        print "Post links to Reddit"
                        bot.write_to_file(submission.id)
                        bot.reset_fields()
                        continue
                except:
                    bot.write_to_file(submission.id)
                    bot.reset_fields()
                    continue

                print("\nXPost found!")
                print("subreddit = " + str(submission.subreddit.display_name.lower()))
                print("post title = " + bot.xpost_title)
                print("xpost_url = " + bot.xpost_url)
                print("xpost_permalink = " + bot.xpost_permalink.encode('utf-8'))

                bot.write_to_file(submission.id)
                bot.get_original_sub()

                if (bot.original_sub_title == None or 
                    bot.original_sub_title == bot.xpost_sub.display_name.lower().encode('utf-8')):
                    print "Failed original subreddit or same subreddit"
                    bot.reset_fields()
                else:
                    if not bot.has_source(submission) and bot.search_for_post(submission, 150):
                        try:
                            bot.create_comment(submission)
                            bot.write_to_file(submission.id)
                            bot.reset_fields()
                        except:
                            print "Failed to comment"
                            bot.write_to_file(submission.id)
                            bot.reset_fields()
                    else:
                        print "Failed to find source"
                        bot.write_to_file(submission.id)
                        bot.reset_fields()
            # the submission is not an xpost or submission id is in cache already
            else:
                bot.reset_fields()

        bot.delete_negative()
        bot.temp_cache.clear()
        bot.xpost_submissions.clear()

        print "\nSleeping\n"
        time.sleep(10)
        if len(bot.cache) > 1000:
            bot.clear_database()
