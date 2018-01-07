import pymysql.cursors
import praw
import re
import time
from prawcore.exceptions import PrawcoreException
from SendDailyReading import sendReading
from config import DEBUG, SUBREDDIT
from dbSettings import settings
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s:%(levelname)s - %(message)s')
fileHandler = logging.FileHandler('./Logs/subM.log')
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)

DEFAULT_PARAGRAPHS = 2
DEFAULT_CHAPTER = 0
DEFAULT_SECTION = 1
DEFAULT_DAY = 1

reddit = praw.Reddit('StoryBot')
stream = reddit.subreddit(SUBREDDIT).stream
connection = pymysql.connect(**settings)
cursor = connection.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def createSubscriptionTable():
    sql = """CREATE TABLE `Subscriptions` (
        `Name` varchar(255),
        `Story_Id` varchar(255) NOT NULL,
        `Chapter` int NOT NULL,
        `Section` int NOT NULL,
        `Last_Read` int NOT NULL,
        `Paragraphs_Per_Read` int NOT NULL,
        `Day` int NOT NULL,
        PRIMARY KEY (Name, Story_Id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ;"""
    try:
        cursor.execute(sql)
    except Exception as error:
        logger.exception('From createSubscriptionTable:')
        pass

def getStoryId(postBody):
    return re.search(r'Link:.*.com/(.+?)/', postBody)[1]

def isSubscribing(myStr):
    match = re.match(r'\s*!subscribe\s*(\d*)\s*', myStr, flags=re.IGNORECASE)
    if not match:
        return None
    paragraphs = match[1] if match[1] and int(match[1]) <= 50 else DEFAULT_PARAGRAPHS
    return {'paragraphs': int(paragraphs)}
    

def findNewSubscribers():
    global connection, cursor
    while True:
        try:
            for comment in stream.comments():
                if DEBUG: print(comment.body)
                submission = comment.submission

                current_time = time.time()
                subscribing = isSubscribing(comment.body)
                if submission.author and submission.author.name == 'JapaneseStoryBot' and subscribing and comment.created_utc + 900 > current_time:
                    story_id = getStoryId(submission.selftext)
                    sql = """INSERT INTO `Subscriptions`
                    (Name, Story_Id, Chapter, Section, Last_Read, Paragraphs_Per_Read, Day)
                    VALUES ('{}', '{}', {}, {}, {}, {}, {});""".format(comment.author.name
                    , story_id, DEFAULT_CHAPTER, DEFAULT_SECTION, int(time.time()), subscribing['paragraphs'], DEFAULT_DAY)
                    if DEBUG:
                        print(sql)

                    successful = False
                    while not successful:
                        try:
                            cursor.execute(sql)
                            connection.commit()
                            sendReading(comment.author.name, story_id)
                            print('Added Subscriber', comment.author.name)
                            successful = True
                        except pymysql.err.IntegrityError:
                            successful = True
                            pass
                        except pymysql.err.OperationalError as e:
                            logger.exception('From changeReadingQuantity')
                            connection = pymysql.connect(**settings)
                            cursor = connection.cursor()
                            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        except PrawcoreException as error:
            logger.exception('From findNewSubscribers:')
            time.sleep(10)






if __name__ == '__main__':
    findNewSubscribers()