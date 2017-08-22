import praw
import kdapi
import time

from datetime import datetime
from random import randint

############################################################
################### Repost-Bot #############################
############################################################
# Searches for reposts and finds the original post.
# Randomly chooses 1st, 2nd, or 3rd top comment from
# original post and writes that comment to the repost
############################################################
############################################################


#----------------------NOTES--------------------------------
#
#   *CODE NOT WORKING: LINES 76-94
#
#----------------------NOTES------------------------------------



#---------------------------------------------------------------

# Subreddits that post images that karmadecay has a hard time with, or they cause undesirable comments by the bot
avoided_subreddits = ['fiveyearsagoonreddit', 'photoshopbattles', 'hotandtrending', 'newsokuvip', 'Tinder'
                      'fireemblemheroes', 'bitcoinall', 'adviceanimals', 'the_donald', 'The_Donald_Discuss', 'subredditsimulator'
                      'subredditsimmeta', 'SubredditSimulator_SS', 'customhearthstone']

# today_date as golbal so only calculated once instead of each time a repost found.
# Need to be put back in getAge() if bot run for long period of time
today_date = datetime.now().date()
punctuations = '\'\"!@#$%^&*()-_=+,.~`/<>?;:[]}{\|-'

#---------------------------------------------------------------
def botLogin():
    r = praw.Reddit('Octopupper')
    return r

#---------------------------------------------------------------
def getAge(original):
    timestamp = original.created
    original_date = datetime.fromtimestamp(timestamp).date()
    age_of_original = today_date - original_date
    return(age_of_original.days)

#---------------------------------------------------------------
def findComment(comment_list):
    # Randomly take the 1st, 2nd, or 3rd comment from original and comment it on repost
    trys = 0
    comment_number = randint(0,2)
    comment_to_post = str(comment_list[comment_number].body)

    # Lines 76-90 not working. It's supposed to go through all top 3 comments and find one that is not '[deleted]' or '[removed]',
    # but if the loop is ever entered, it will always return 0.
    while ('[deleted]' in comment_to_post or '[removed]' in comment_to_post) and trys < 3:
        if comment_number == 0:
            comment_number == 1

        elif comment_number == 1:
                comment_number ==2

        else:
            comment_number == 0

        trys += 1
        comment_to_post = str(comment_list[comment_number].body)

    if trys == 3:
        return(0)

    # Check for 'edit' in comment. If an edit exists, remove 'edit' and every word after it
    else:
        no_punctuation = ""
        for char in comment_to_post:
            if char not in punctuations:
                no_punctuation += char

        temp_comment = no_punctuation.lower()
        if 'edit' in temp_comment:
            comment_list = comment_to_post.split()
            temp_list = temp_comment.split()

            i = 0
            while 'edit' not in temp_list[i]:
                i += 1

            new_comment = comment_list[:i]
            new_comment = ' '.join(new_comment)
            return(new_comment)

        else:
            return(comment_to_post)




#---------------------------------------------------------------
def printComment(submission, original, reddit, comment_to_post):
    print("\n *Found Comment to Post: '{}'".format(comment_to_post))
    reply = submission.reply(comment_to_post)
    submission.upvote() #for better chance of submission getting higher
    print(" *Link to Comment Made by Bot: http://reddit.com{}".format(reply.permalink()))
    reddit.redditor('Octopupper').message('Comment Made', 'Comment Link: {} Original Post Link: {}'.format(reply.permalink(), original.shortlink))
    #time.sleep(300) #use if karma on account isn't high enough, won't run into ratelimit w/ higher karma


#----------MAIN---------------------------------------------
def main():
    reddit = botLogin()
    sub = reddit.subreddit('all')

    # Get new reddit post
    for submission in sub.stream.submissions():
        if "imgur" in submission.url and submission.subreddit not in avoided_subreddits:
            if submission.over_18:  #ignore nsfw posts
                continue

            print("\n-------------------------------------------------------")
            print("Checking Submission in /r/{}".format(submission.subreddit))

            # Check karmadecay to see if repost
            try:
                links_list = []
                for item in kdapi.check(submission.url):
                    links_list.append(item.link)
                num_of_originals = len(links_list)
            except:
                print("CONNECTION ERROR, skipping submission...")
                continue

            if num_of_originals > 0:
                print("     Repost Found!: {}".format(submission.shortlink))
                print("\n     Number of Originals: {}\n".format(num_of_originals))

                # Get comments and age of original post
                for link in links_list:
                    comment_list = []
                    original = reddit.submission(url=link)
                    original_age = getAge(original)

                    for top_level_comment in original.comments:
                        comment_list.append(top_level_comment)

                    print("     Original Post Link: {}".format(original.shortlink))
                    print("     Number of Comments: {}".format(len(comment_list)))
                    print("     Age of Post: {} days old".format(original_age))

                    # Remember: coment_list holds the number of top level comments, not total number of comments
                    if len(comment_list) > 24 and original_age > 29:
                        try:
                            comment_to_post = findComment(comment_list)
                            if comment_to_post == 0:
                                print("Skipping post due to only '[deleted]' or '[removed]' comments")
                                break
                            else:
                                printComment(submission, original, reddit, comment_to_post)

                        except praw.exceptions.APIException as ratelimit:
                            print(ratelimit)
                            reddit.redditor('Octopupper').message('I Reached the RateLimit', 'Maybe you should play with the sleep timer... ')

                        break # W/out break, bot makes many comments on repost if many originals exist

            else:
                print("     Not a Repost")




if __name__ == '__main__':
    main()
