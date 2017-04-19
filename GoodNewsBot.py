import praw
# import json
# import requests
import time
import indicoio
import sys
import hiddensettings

indicoio.config.api_key = hiddensettings.indicoio_api_key

user_agent=hiddensettings.user_agent
client_id=hiddensettings.client_id
client_secret=hiddensettings.client_secret
username=hiddensettings.username
pword=hiddensettings.pword

subreddittoread='worldnews+worldnews_uk+news'
subreddittowrite='justgoodnews'
new_post_limit=250

def main():
    subreddit = setup_connection_reddit(subreddittoread)
    getsubmissions(subreddit)


def setup_connection_reddit(subreddit):
    print("[bot] setting up connection with Reddit")
    reddit = praw.Reddit(user_agent=user_agent, client_id=client_id, client_secret=client_secret, username=username, password=pword)
    subreddit = reddit.subreddit(subreddittoread)
    return subreddit


def getsubmissions(subreddit_info):
    post_dict = {}
    post_dict_dirtyurl = {}
    print("[bot] Requesting {} posts from reddit.com/r/{}/new".format(new_post_limit, subreddittoread))
    for submission in subreddit_info.new(limit=new_post_limit):
        dirtyurl = submission.url
        newurl = clean_url(submission.url)
        newtitle = clean_title(submission.title)
        found = duplicate_check_url(newurl)
        if found == 0:
            post_dict[newtitle] = clean_url(submission.url)
            post_dict_dirtyurl[newtitle] = submission.url
            add_url_to_file(newurl)
            
    print("[bot] Analysising sentiment for {} new posts".format(len(post_dict)))
    
    for post in post_dict:
        post_title = post
        post_link = post_dict[post]
        post_link_dirty = post_dict_dirtyurl[post]
        ispositive = sentiment(post_link_dirty, post_title)
        if "pos -" in ispositive:
            print("[bot] Pos news - {} - {} - {}".format(ispositive, post_title, post_link))
            score = ispositive.replace("pos -", "")
            goodnewspost(post, post_link_dirty, score)
        else:
            print("[bot] NOT Pos news - {} - {} - {}".format(ispositive, post_title, post_link))


def goodnewspost(post_title, post_url, score):
    reddit = praw.Reddit(user_agent=user_agent, client_id=client_id, client_secret=client_secret, username=username, password=pword)
    print("[bot] Posting {} - {} - to /r/{} (positivity = {})".format(post_title, post_url, subreddittowrite, score))
    post = reddit.subreddit(subreddittowrite).submit(title=post_title, url=post_url)
    post.mod.flair(text="Positivity={}".format(score))
    # time.sleep(10)


def sentiment(link, title):
    # r = requests.post('http://text-processing.com/api/sentiment/', data = {'text': title})
    # posnegneutral = json.loads(r.text)['label']
    
    try:
        link_pos = indicoio.sentiment_hq(link)
        if link_pos > 0.9:
            # save an API call 
            # - don't need to waste one if page contents already > 0.9 (pos)
            title_pos = link_pos
        else:
            title_pos = indicoio.sentiment_hq(title)
        
        avg_pos = (link_pos + title_pos) / 2
        
        if avg_pos > 0.8:
            posnegneutral = "pos - {} (avg)".format(avg_pos)
        elif link_pos > 0.9 or title_pos > 0.9:
            posnegneutral = "pos - {} (max)".format(max(avg_pos))
        elif link_pos < 0.5 or title_pos < 0.5:
            posnegneutral = "neg - {} (avg)".format(avg_pos)
        else:
            posnegneutral = "neutral (link_pos={} title_pos={} avg={})".format(link_pos, title_pos, avg_pos)
            
    except:
        e = sys.exc_info()
        posnegneutral = "ERROR Checking Sentiment: {}".format(e)
    
    return posnegneutral


def duplicate_check_url(url):
    found = 0
    with open('posted_posts_urls.txt', 'r') as file:
        for line in file:
            if url in line:
                found = 1
    return found


def add_url_to_file(url):
    with open('posted_posts_urls.txt', 'a') as file:
        file.write(str(url) + "\n")


def clean_url(url):
    newurl = url.replace(u"https://", "").replace(u"http://", "").replace(u"www.", "").replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u" ", "").replace(u"\n", "")
    return newurl


def clean_title(title):
    newtitle = title.replace(u"\u2018", "'").replace(u"\u2019", "'").encode("ascii", "replace")
    return newtitle


if __name__ == '__main__':
    main()
