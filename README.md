# Reddit Original Post Searcher Bot
[OriginalPostSearcher](https://www.reddit.com/user/OriginalPostSearcher/)  
A Reddit bot that aims to comment with the original submission of an xpost  

Made as a practice bot with Python for [Reddit](http://www.reddit.com/). I wanted to make something for fun to learn a bit more about Python and databases.  
Thanks to [stackoverflow](http://stackoverflow.com/), [/r/learnpython](http://www.reddit.com/r/learnpython), and [/r/python](http://www.reddit.com/r/python)

The format for a response is:
```
XPost from (subreddit with link)  
(submission title with link)
```

## TODO
- Do something to deal with unwanted comments (Completed 7/15/2015)
- Clean up code for pep8
- Continue to update/optimize bot
- Continue to update the list of ignored subreddits

## Updates
```
1.0.1 (7/15/2015) - Fixed commenting bug that involved the wrong links and added ability to delete unwanted comments  
1.0.2 (7/16/2015) - Fixed a string checking bug for utf-8 and added logging/print statements  
1.0.3               Updated the order of finding the original post, check for content first
1.0.4 (7/17/2015) - Changed the return value of one of the variables, added more logging, updated ignoredSubs list/function names
1.0.5 (7/18/2015) - Added source check, renamed old user_agent from old files, and updated ignoredSubs list
1.0.6               Updated source checking, updated user_agent, removed searchedPosts.txt, and updated ignoredSubs list
1.0.7 (7/19/2015) - Added check if getting subreddit failed, changed comment style, and updated ignoredSubs list
1.0.8 (7/20/2015) - Changed commenting style/words, updated ignoredSubs list
1.0.9             - Code cleanup, updated ignoredSubs list
1.1.0 (7/21/2015) - Added new function to find the original post faster (doesn't cover self-posts), updated ignoredSubs list
1.1.1             - Cleaned up code, updated ignoredSubs list
1.1.2 (7/22/2015) - Added original poster's username for commenting
1.1.3 (7/25/2015) - Fixed checking original post bug that involved "in" phrase, updated commenting to emphasize convenience for
                    mobile users, and updated ignoredSubs list
1.1.4 (7/29/2015) - Added ability to create no participation links for certain subreddits
```
