import praw
import time
from config import SUBREDDIT
from prawcore.exceptions import PrawcoreException
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s:%(levelname)s - %(message)s')
fileHandler = logging.FileHandler('./Logs/FlairS.log')
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)

reddit = praw.Reddit('StoryBot')
stream = reddit.subreddit(SUBREDDIT).stream
STORY_FLAIR_ID = 'e57e87fa-dc80-11e7-80c2-0eaeaf19a214'


def flairStories():
    while True:
        try:
            for submission in stream.submissions():
                if submission and submission.author.name == 'JapaneseStoryBot':
                    submission.flair.select(STORY_FLAIR_ID)
        except PrawcoreException as error:
            logger.exception('From flairStories:')
            time.sleep(10)





