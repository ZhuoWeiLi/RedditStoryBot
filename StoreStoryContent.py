import pymysql.cursors
import lxml.html
import requests
import re
from StoryScraper import getStoryId
from dbSettings import settings
import logging
import time

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s:%(levelname)s - %(message)s')
fileHandler = logging.FileHandler('./Logs/StoreS.log')
fileHandler.setFormatter(formatter)

connection = pymysql.connect(**settings)
cursor = connection.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def createStoryContentTable():
    sql = """CREATE TABLE `StoryContent` (
        `Id` varchar(255) NOT NULL,
        `Chapter` int NOT NULL,
        `Section` int NOT NULL,
        `Paragraph` text NOT NULL,
        PRIMARY KEY (Id, Chapter, Section)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ;"""
    try:
        cursor.execute(sql)
    except:
        pass

# Splits a long string enough arrays of paragraphs longer than 50 characters
def splitText(text):
    paragraphs = text.split('\n\n')
    res = []
    i = 0
    while i < len(paragraphs):
        new_paragraph = ''
        while (len(new_paragraph) < 50 and i < len(paragraphs)) or i == len(paragraphs) - 1 :
            new_paragraph += paragraphs[i] + "\n\n"
            i += 1
        res.append(new_paragraph)
    return res




# Takes a story chapter and populates an sql table
# after splitting the content into paragraphs
def populateStoryContent(url):
    global connection, cursor
    try:
        r = requests.get(url)
        html = lxml.html.fromstring(r.content)
        chapterText = html.cssselect('#novel_honbun')[0].text_content()
    except IndexError:
        return False
    story_id = getStoryId(url)
    chapter = re.search(r'.*/(\d+)/', url)[1]
    paragraphs = splitText(chapterText)

    for i in range(len(paragraphs)):
        successful = False
        while not successful:
            try:
                sql = """INSERT INTO `StoryContent`
                (Id, Chapter, Section, Paragraph)
                VALUES ('{}', {}, {}, '{}');""".format(story_id, chapter, i+1, paragraphs[i])
                cursor.execute(sql)
                print(sql)
                connection.commit()
                successful = True
            except pymysql.err.OperationalError:
                logging.exception('From populateStoryContent Operational Err')
                connection = pymysql.connect(**settings)
                cursor = connection.cursor()
                cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

            except pymysql.err.InternalError:
                logging.exception('From populateStoryContent Internal Err')
                time.sleep(10)

    

