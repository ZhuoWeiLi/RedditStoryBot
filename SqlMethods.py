from StoryScraper import getStoryInfo, rankings
from config import DEBUG
import pymysql.cursors
import time
from dbSettings import settings
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s:%(levelname)s - %(message)s')
fileHandler = logging.FileHandler('./Logs/sqlM.log')
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)


connection = pymysql.connect(**settings)
cursor = connection.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def createStoryTable():
    sql = """CREATE TABLE `Stories` (
        `Id` varchar(255) PRIMARY KEY,
        `Link` varchar(255) NOT NULL,
        `Title` varchar(255) NOT NULL,
        `Summary` text NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;"""
    try:
        cursor.execute(sql)
    except:
        pass

def populateDB():
    for url in rankings:
        for story in getStoryInfo(url):
            try:
                sql = """INSERT INTO Stories
                (Id, Link, Title, Summary)
                VALUES (%s, %s, %s, %s);"""
                cursor.execute(sql, story)
                connection.commit()
            except Exception as error:
                logger.exception('From populateDB:' + str(error))

    if DEBUG:
        print('finished populating DB')

def populateInterval(interval):
    while True:
        populateDB()
        time.sleep(interval)



def chooseStoryById(story_id):
    sql = """SELECT * 
    FROM `Stories` 
    WHERE `Id` = '{}'""".format(story_id)
    try:
        cursor.execute(sql)
    except Exception as error:
        logger.exception('From chooseStoryById:')
        pass
    return cursor.fetchone()


def chooseRandStory():
    sql = """SELECT * 
    FROM `Stories` 
    ORDER BY RAND ()
    LIMIT 1"""
    try:
        cursor.execute(sql)
    except Exception as error:
        logger.exception('From chooseRandStory:')
        return
    return cursor.fetchone()
