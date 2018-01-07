import praw
import re
import time
from config import DEBUG, SUBREDDIT
from SqlMethods import chooseRandStory

reddit = praw.Reddit('StoryBot')


postTemplate = """{} \n\n&nbsp;\n\n Link: {}"""
subreddit = reddit.subreddit(SUBREDDIT)

def formatLineBreaks(myStr):
    def repl(matchObj):
        res = '\n\n'
        numLines = matchObj[0].count('\n')
        if numLines == 1:
            return '  \n'
        elif numLines == 2:
            return '\n\n&nbsp;\n\n'
        else:
            for i in range(numLines-1):
                res = '\n\n&nbsp;' + res
            return res

    return re.sub('\n+', repl, myStr)

def postStory():
    story = chooseRandStory()
    if not story:
        return
    summary, link = story[3], story[1]
    summary = formatLineBreaks(summary)
    postBody = postTemplate.format(summary, link)
    subreddit.submit(story[2], postBody)
    if DEBUG:
        print('finished posting story')

def postInterval(interval):
    while True:
        postStory()
        time.sleep(interval)

