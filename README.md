# RedditStoryBot

Reddit Bot for pulling stories from http://yomou.syosetu.com/rank/top/

## How to Run

Enter your settings into config.py, praw.ini (Reddit credentials) and dbSettings.py (MySQL database credentials) 

```bash
git clone https://github.com/ZhuoWeiLi/RedditStoryBot/
cd RedditStoryBot
```
Create your initial sql tables using initializeTables.sql

```bash
pip install pymysql requests lxml cssselect praw 
python Main.py
```
