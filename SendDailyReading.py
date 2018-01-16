import pymysql.cursors
import praw
import time
from StoryPoster import formatLineBreaks
from StoreStoryContent import populateStoryContent
from dbSettings import settings
from config import DEBUG, SUBREDDIT
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s:%(levelname)s - %(message)s')
fileHandler = logging.FileHandler('./Logs/SendD.log')
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)


sendingFrequency = 86400

linkBase = 'https://ncode.syosetu.com/'

reddit = praw.Reddit('StoryBot')

connection = pymysql.connect(**settings)
cursor = connection.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def changeChapter(name, story_id):
    sql = """UPDATE `Subscriptions`
    SET Chapter = Chapter + 1, Section = 1
    WHERE Name = '{}' AND Story_Id = '{}';""".format(name, story_id)
    cursor.execute(sql)
    connection.commit()


def deleteSubscription(name, story_id):
    sql = """DELETE FROM `Subscriptions`
    WHERE Name = '{}' AND Story_Id = '{}';""".format(name, story_id)
    try:
        cursor.execute(sql)
        if DEBUG:
            print('is unsubscribing:', name, story_id)
        subject = 'Unsubscribing From Story {}'.format(story_id)
        message = 'You have successfully unsubscribed from this story.'
        reddit.redditor(name).message(subject, message)
        connection.commit()
    except Exception as error:
        logger.exception('From deleteSubscription:' + str(error))
        pass



def getTitle(story_id):
    sql = """SELECT Title FROM `Stories`
    WHERE Id = '{}'""".format(story_id)
    if DEBUG:
        print(sql)
    cursor.execute(sql)
    res = cursor.fetchone()
    if res is not None:
        return res[0]
    else:
        return None



def incrementSection(name, story_id, paragraphs_per_read):
    global connection, cursor
    sql = """UPDATE `Subscriptions`
    SET Section = Section + {}, Last_Read = {}, Day = Day + 1
    WHERE Name = '{}' AND Story_Id = '{}';""".format(paragraphs_per_read, int(time.time()) + sendingFrequency, name,
                                                     story_id)
    successful = False
    while not successful:
        try:
            cursor.execute(sql)
            connection.commit()
            successful = True
        except pymysql.err.OperationalError as e:
            logger.exception('From incrementSection:')
            connection = pymysql.connect(**settings)
            cursor = connection.cursor()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")




def getReading(story_id, chapter, section, paragraphs):
    sql = """SELECT * FROM `StoryContent`  
    WHERE Id = '{}' AND Chapter = {} AND Section >= {} AND Section < {};"""
    if DEBUG:
        print(sql.format(story_id, chapter, section, section + paragraphs))
    cursor.execute(sql.format(story_id, chapter, section, section + paragraphs))
    res = cursor.fetchall()
    if DEBUG:
        print(res)
    return res

def sendReading(username, story_id):
    global cursor, connection
    sql = """SELECT * FROM `Subscriptions`
    WHERE Name = '{}' AND Story_Id = '{}';""".format(username, story_id)
    successful = False
    while not successful:
        try:
            cursor.execute(sql)
            successful = True
        except (pymysql.err.OperationalError, TimeoutError):
            logger.exception('From sendReading:')
            connection = pymysql.connect(**settings)
            cursor = connection.cursor()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

    subscription = cursor.fetchone()
    if subscription is not None:
        story_id, chapter, section = subscription[1:4]
        paragraphs, day = subscription[5:7]
        res = getReading(story_id, chapter, section, paragraphs)
        story_title = getTitle(story_id)

        storyDone = False

        # Reached the end of the previous chapter, so the query returns nothing
        if not res:
            # Change the chapter and query again
            changeChapter(username, story_id)
            chapter += 1
            section = 1


            if populateStoryContent(linkBase + story_id + '/' + str(chapter) + '/') is False:
                # We are out of chapters, so we've reached the end of the story
                message = """It appears this story has reached its end 
                            either temporarily or permanently. We hope you enjoyed spending your time reading!"""
                reddit.redditor(username).message('End: {}'.format(story_title), message)
                deleteSubscription(username, story_id)
                storyDone = True

            res = getReading(story_id, chapter, section, paragraphs)

        if not storyDone and res:
            incrementSection(username, story_id, paragraphs)
            chapter_url = linkBase + story_id + '/' + str(chapter) + '/'
            subject = "{}: Day {} - Chapter {} ".format(story_id, day, chapter)

            paragraphs = ''

            for i in range(len(res)):
                paragraphs += res[i][3]
            paragraphs = formatLineBreaks(paragraphs)
            # + '\n\n&nbsp;\n\nChapter Link: ' + chapter_url
            message = paragraphs
            if DEBUG: print(message)
            reddit.redditor(username).message(subject, message)
            if DEBUG:
                print('reading Sent')

#Send reading to those who have gone 24 hrs since their last reading
def sendReadingAll():
    sql = """SELECT * FROM `Subscriptions`;"""
    cursor.execute(sql)
    current_time = int(time.time())
    for subscription in cursor.fetchall():
        if DEBUG: print('checking subscription', subscription)
        last_read = subscription[4]
        if DEBUG: print(current_time, last_read)
        if current_time >= last_read:
            name, story_id = subscription[0:2]
            sendReading(name, story_id)

def sendInterval(interval):
    while True:
        sendReadingAll()
        time.sleep(interval)

