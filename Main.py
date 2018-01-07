from StoryPoster import postInterval
from SqlMethods import populateInterval
from SubscriberManager import findNewSubscribers
from MonitorMessages import checkInbox
from SendDailyReading import sendInterval
from FlairStories import flairStories
import threading
import time


POSTINGINTERVAL = 3600
POPULATEINTERVAL = 86400
SENDINGINTERVAL = 300
threads = []
threads.append(threading.Thread(target=sendInterval, args=(SENDINGINTERVAL,)))
threads.append(threading.Thread(target=populateInterval, args=(POPULATEINTERVAL,)))
threads.append(threading.Thread(target=postInterval, args=(POSTINGINTERVAL,)))
threads.append(threading.Thread(target=findNewSubscribers))
threads.append(threading.Thread(target=checkInbox))

threads.append(threading.Thread(target=flairStories))

for t in threads:
    t.start()



