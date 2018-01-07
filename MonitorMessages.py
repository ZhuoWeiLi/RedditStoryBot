import pymysql.cursors
import praw
import re
import time
from SendDailyReading import getTitle, deleteSubscription, sendReading
from dbSettings import settings
from config import DEBUG, SUBREDDIT
from prawcore.exceptions import PrawcoreException
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s:%(levelname)s - %(message)s')
fileHandler = logging.FileHandler('./Logs/MonitorM.log')
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)

connection = pymysql.connect(**settings)
cursor = connection.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
reddit = praw.Reddit('StoryBot')

def isUnsubscribing(myMessage):
    match = re.match(r'\s*!unsubscribe\s+(\w+)\s*', myMessage, flags=re.IGNORECASE)
    if match:
        return {'story_id': match[1]}
    return None


def isChangingReadingQuantity(myMessage):
    match = re.match(r'\s*!Reading\s*Quantity\s+(\w+)\s+(\d+)\s*', myMessage, flags=re.IGNORECASE)
    if match and int(match[2]) <= 50:
        if DEBUG: print('Found match for readingquantity', match[0])
        return {'story_id': match[1], 'reading_quantity': int(match[2])}
    return None


def changeReadingQuantity(name, story_id, newQuantity):
    global connection, cursor
    sql = """UPDATE `Subscriptions`
    SET Paragraphs_Per_Read = {}
    WHERE Name = '{}' AND Story_Id = '{}';""".format(newQuantity, name, story_id)
    successful = False
    while not successful:
        try:
            if DEBUG:
                print(sql)
            cursor.execute(sql)
            title = getTitle(story_id)
            subject = 'Changing Daily Reading Quantity to {} for Story {}'.format(newQuantity, story_id)
            message = 'You have successfully changed your daily reading quantity.'
            reddit.redditor(name).message(subject, message)
            if DEBUG:
                print('changed quantity of', name, story_id, newQuantity)
            connection.commit()
            successful = True
        except pymysql.err.OperationalError as e:
            logger.exception('From changeReadingQuantity')
            connection = pymysql.connect(**settings)
            cursor = connection.cursor()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")



def isNextReading(myMessage):
    match = re.match(r'\s*!Next\s*Reading\s+(\w+)\s*', myMessage, flags=re.IGNORECASE)
    if match:
        return {'story_id': match[1]}
    return None




def checkInbox():
    while True:
        try:
            for message in reddit.inbox.stream():
                current_time = time.time()
                if message.created_utc + 900 > current_time:
                    print('new message:', message.body)
                    unsubscribing = isUnsubscribing(message.body)
                    changingQuantity = isChangingReadingQuantity(message.body)
                    nextReading = isNextReading(message.body)
                    author = message.author.name
                    if unsubscribing:
                        story_id = unsubscribing['story_id']
                        deleteSubscription(author, story_id)
                    elif changingQuantity:
                        story_id, newQuantity = changingQuantity['story_id'], changingQuantity['reading_quantity']
                        changeReadingQuantity(author, story_id, newQuantity)
                    elif nextReading:
                        story_id = nextReading['story_id']
                        sendReading(author, story_id)
        except PrawcoreException as error:
            logger.exception('From checkInbox')
            time.sleep(10)

if __name__ == '__main__':
    checkInbox()