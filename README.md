# Reddit Original Post Searcher Bot
[OriginalPostSearcher](https://www.reddit.com/user/OriginalPostSearcher/)  
A Reddit bot that aims to comment with the original submission of an xpost  

Made as a practice bot with Python for [Reddit](http://www.reddit.com/). I wanted to make something for fun to learn a bit more about Python and databases.  
Thanks to [stackoverflow](http://stackoverflow.com/), [/r/learnpython](http://www.reddit.com/r/learnpython), and [/r/python](http://www.reddit.com/r/python)

The format for a response is:
```
Original post referenced from /r/subreddit by /u/user
*submission title with link*
```  
## FAQ
**What's the point of this bot?**  
The bot's purpose is to provide a sort of convenience and sourcing tool for x-posts that occur daily on Reddit. With this bot's comments, the referenced post in an x-post and its author is credited. It also helps save a few clicks, especially for mobile users.  
  
**How does it work?**  
Basically, the bot looks to find any submission with that might be an x-post, tries to see if it can find the original submission in the subreddit mentioned in the title *e.g. Title of post! (xpost from /r/specific_subreddit)*, and comments to the x-post the title of original submission, the author of that submission, its subreddit, and a link to the original submission. The bot is hosted on Heroku.  
  
**What's the point if there's the "other discussions" tab?**  
I actually did not realize that there was an "other discussions" tab until it was pointed out when this bot was commenting. At that point, I thought that there was actually no point for this bot due to that tab. However, I had a lot of positive reception (futher down the page) and there was the benefit of providing a quick link for mobile users. With that, I decided to continue development of the bot, saving Redditors a few clicks and providing proper crediting.  
  
**What about brigading for subreddits that require "np" links?**  
There is a list of subreddits that the bot provides "np" links -  [nopart.py](https://github.com/papernotes/Reddit-OriginalPostSearcher/blob/master/nopart.py)  
There is also a list of subreddits that the bot will not comment to -  [ignoredSubs.py](https://github.com/papernotes/Reddit-OriginalPostSearcher/blob/master/ignoredSubs.py)  
  
**Can I provide a suggestion?**  
Of course! PM [/u/OriginalPostSearcher](https://www.reddit.com/user/OriginalPostSearcher/), and I'll be happy to look into it.
  
# Reception  
### Positive
*This is my new favourite bot!* - [Kvothealar](https://www.reddit.com/r/shittyrobots/comments/3ful9e/the_tiniest_firefighter_xpost_rgifs/cts9azi?context=3)  
*I like this bot. Whoever came up with it did good.* - [CaseH1984](https://www.reddit.com/r/retrogaming/comments/3fsrds/xpost_from_rgaming_guy_3d_prints_a_tiny_nes_case/ctrlm2c?context=3)  
*THE SECOND COMING OF REPOST STATISTICS?! THE PRODIGAL SON HAS RETURNED!* - [StaticDraco](https://www.reddit.com/r/funny/comments/3fn5ds/cop_frees_baby_skunk_from_yogurt_container_xpost/ctql2ey?context=3)  
*At least the bot gave me credit for my photo :)* - [FoodandFrenchies](https://www.reddit.com/r/burgers/comments/3fo5jb/bacon_avocado_bison_cheeseburger_on_a_homemade/ctqege2?context=3)  
*I fucking love the bots in this sub. There's a sentence I never thought I'd see myself type.* - [Takatalvi_Ignatio](https://www.reddit.com/r/deathgrips/comments/3flirt/ive_been_playing_waaaay_too_much_poe_for_this_to/ctq3pru?context=3)  
*Thank you bot. What would we do without you.* - [LordZikarno](https://www.reddit.com/r/ElderScrolls/comments/3fmo4f/interesting_reference_ive_found_in_skyrim_xpost/ctpz6a0?context=3)  
*I'd recommend not banning that bot, he's quite useful.* - [Chastlily](https://www.reddit.com/r/fireemblem/comments/3fimvt/hey_guys_i_recently_made_a_fire_emblem_radiant/ctoy96s?context=3)  
*This bot is awesome* - [Ninja_Fox_](https://www.reddit.com/r/linuxmasterrace/comments/3flqtj/wipes_windows_in_seconds_xpost_from_rfunny/ctpsbns?context=3)  
*I appreciate that.* - [FaceReaityBot](https://www.reddit.com/r/wethebest/comments/3flnm9/go_buy_your_whole_family_something_nice_xpost/ctpqhag?context=3)  
*thank mr bot for good xposts and lack of calcium* - [Poyoarya](https://www.reddit.com/r/shittyreactiongifs/comments/3fkgwt/mfw_i_realize_i_forgot_my_skeleton_at_home_xpost/ctpgl58?context=3)  
*Thank you for tagging me botfriend <3* - [throwcap](https://www.reddit.com/r/shockwaveporn/comments/3fj9wd/missile_hitting_its_target_xpost_from_rvideos_10s/ctp3xbi?context=3)  
*Ooh, that's a cool bot.* - [Non-Alignment](https://www.reddit.com/r/fireemblem/comments/3fimvt/hey_guys_i_recently_made_a_fire_emblem_radiant/ctoxpqs?context=3)  
*Wow, what a useful bot I never knew existed :O* - [mnmnmnmn1](https://www.reddit.com/r/TheBluePill/comments/3fc9qs/gaylubeoil_gets_into_a_dickwaving_contest_with/ctnpdvd?context=3)  
*Ahh you beat me to it. Excellent bot, this.* - [critically_damped](https://www.reddit.com/r/LaserCats/comments/3f91ql/allweather_lasercat_xpost_from_rcatloaf/ctmfwrr?context=3)  
*I think this bot addresses every possible problem with reposting.* - [winter_mutant](https://www.reddit.com/r/ContagiousLaughter/comments/3f1mn6/okay_google_whats_a_blumpkin_xpost_from/ctky10v?context=3)  
*Well that is a nifty bot.* - [davidverner](https://www.reddit.com/r/AmIFreeToGo/comments/3f1r2u/crosspost_from_rroadcam_driver_smashes_into_cars/ctkqbb1?context=3)  
*Hey, I kind of like this. Kudos bot.* - [NewJerseyFreakshow](https://www.reddit.com/r/TopMindsOfReddit/comments/3eq9a4/top_mind_mod_of_coontown_ueugenenix_gets_demodded/cthd8qy?context=3)  
*What a lovely bot.* - [kevik72](https://www.reddit.com/r/funny/comments/3efuvp/trick_friends_into_thinking_you_have_your_shit/cteiy59?context=3)  
*Keep up the good work* - [Xfactor5492](https://www.reddit.com/r/CrappyDesign/comments/3ebgyz/girlfriend_wasnt_sure_why_i_laughed_at_her_water/ctdcc4j?context=3)  
*See, the bot knows how to crosspost. Why can't we all?* - [Duke_Wintermaul](https://www.reddit.com/r/Nerf/comments/3dsi5g/finally_xpost_from_rgifs/ct8t6bx?context=3)  
*Woah, that's super helpful. I've never seen the x-post bot work like this.* - [jimmycthatsme](https://www.reddit.com/r/woodworking/comments/3e7vja/my_buddy_alan_is_a_woodworker_was_told_his_work/ctcb83q?context=3)

### Not as positive  
*I hate this bot.* - [MightyDebo](https://www.reddit.com/r/ElderScrolls/comments/3fmo4f/interesting_reference_ive_found_in_skyrim_xpost/ctqigu7?context=3)  
*Please die mr bot* - [Lurkerphile](https://www.reddit.com/r/skyrim/comments/3fdt5d/i_guess_nazeem_wasnt_as_important_as_he_thought/ctnwrh5?context=3)  
*Is this bot really necessary? Can't people just click "other discussions" to see this?* - [send-me-to-hell](https://www.reddit.com/r/linux/comments/3f2cix/continual_testing_of_mainline_linux_kernels_xpost/ctkozdh?context=3)  
*Yeah, we know how to use "other discussions" tab.* - [nakilon](https://www.reddit.com/r/MyPeopleNeedMe/comments/3er1yu/battlefield_4_impressive_helicopter_physics_xpost/cthknhm?context=3)  
  
And many "you have been banned from posting to /r/____"
  

**Favorite Thread** - [Googling Recursion](https://www.reddit.com/r/nevertellmetheodds/comments/3f8kt3/xpost_rnevertellmetheodds_this_truck_drifting_on/ctmc72u?context=3)

## TODO
- Do something to deal with unwanted comments (Completed 7/15/2015)
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
1.1.5 (7/30/2015) - Added ability to look through poster's previous posts to save time searching
```
