# Reddit Original Post Searcher Bot
A Reddit bot that aims to comment with the original submission of an xpost  

Made as a practice bot with Python for [Reddit](http://www.reddit.com/). I wanted to make something for fun to learn a bit more about Python and databases   
Thanks to [stackoverflow](http://stackoverflow.com/), [/r/learnpython](http://www.reddit.com/r/learnpython), and [/r/python](http://www.reddit.com/r/python)

The format for a response is:
```
XPost from (subreddit with link)  
(submission title with link)
```

## TODO
- Do something to deal with unwanted comments (Completed 1/15/2015)
- Clean up code for pep8
- Continue to update/optimize bot
- Continue to update the list of ignored subreddits

## Updates
```
1.0.1 (1/15/2015) - Fixed commenting bug that involved the wrong links and added ability to delete unwanted comments  
1.0.2 (1/16/2015) - Fixed a string checking bug for utf-8 and added logging/print statements  
1.0.3               Updated the order of finding the original post, check for content first
1.0.4 (1/17/2015) - Changed the return value of one of the variables, added more logging, updated ignoredSubs list/function names
1.0.5 (1/17/2015) - Added source check, renamed old user_agent from old files, and updated ignoredSubs list
```
