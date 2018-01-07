import lxml.html
import requests
import re

storyBase = "http://yomou.syosetu.com/rank/list/type/"
daily = storyBase + "daily_total/"
weekly = storyBase + "weekly_total/"
monthly = storyBase + "monthly_total/"
quarterly = storyBase + "quarter_total/"
yearly = storyBase + "yearly_total/"
total = storyBase + "total_total/"
rankings = [daily, weekly, monthly, quarterly, yearly, total]

# Given the url of a rankings page, get the (id, links, title, summary)  to the
# top n stories on that page

def getStoryId(link):
    return re.search(r'.*.com/(.+?)/', link)[1]



def getStoryInfo(url, n = 100):
    r = requests.get(url)
    html = lxml.html.fromstring(r.content)
    stories = html.cssselect('.ranking_list')[0:n]
    res = []
    for story in stories:
        header = story.cssselect('.tl')[0]
        title = header.text_content()
        link = header.get('href')
        story_id = getStoryId(link)
        summary = story.cssselect('.ex')[0].text_content()
        res.append((story_id, link, title, summary))
    return res


