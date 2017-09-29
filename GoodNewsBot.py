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

subreddit_to_read='worldnews+worldnews_uk+news'
subreddit_to_write_good='justgoodnews'
subreddit_to_write_bad='justbadnews'
new_post_limit=1000

def main():
    subreddit = setup_connection_reddit(subreddit_to_read)
    getsubmissions(subreddit)


def setup_connection_reddit(subreddit):
    print("[bot] setting up connection to Reddit")
    reddit = praw.Reddit(user_agent=user_agent, client_id=client_id, client_secret=client_secret, username=username, password=pword)
    subreddit = reddit.subreddit(subreddit_to_read)
    return subreddit


def getsubmissions(subreddit_info):
    post_dict = {}
    post_dict_dirtyurl = {}
    print("[bot] Requesting {} posts from reddit.com/r/{}/hot".format(new_post_limit, subreddit_to_read))
    for submission in subreddit_info.hot(limit=new_post_limit):
        dirtyurl = submission.url
        newurl = clean_url(submission.url)
        newtitle = clean_title(submission.title)
        found = duplicate_check_url(newurl)
        if found == 0:
            try:
                add_url_to_file(newurl)
                post_dict[newtitle] = clean_url(submission.url)
                post_dict_dirtyurl[newtitle] = submission.url
            except:
                print("Error: Could not add url to file - {}".format(str(newurl).encode("ascii", "replace")))
            
    print("[bot] Analysising sentiment for {} new posts".format(len(post_dict)))
    
    for post in post_dict:
        post_title = str(post.decode("ascii", "replace"))
        post_link = post_dict[post].encode("utf-8")
        post_link_dirty = post_dict_dirtyurl[post]
        posnegneutral, link_pos, title_pos, avg_pos = sentiment(post_link_dirty, post_title)
        score = posnegneutral.replace("pos -", "").replace("neg -", "")
        if "pos -" in posnegneutral:
            print("[bot] POS news - {} - {} - {}".format(posnegneutral, post_title, post_link))
            newnewspost(post_title, post_link_dirty, score, subreddit_to_write_good)
        elif "neg -" in posnegneutral:
            print("[bot] NEG news - {} - {} - {}".format(posnegneutral, post_title, post_link))
            newnewspost(post_title, post_link_dirty, score, subreddit_to_write_bad)
        elif "ERROR Checking" in posnegneutral:
            print("[bot] ERROR - {}".format(posnegneutral))
        else:
            print("[bot] NEUTRAL news - {} - {} - {}".format(posnegneutral, post_title, post_link))


def newnewspost(post_title, post_url, score, subreddit):
    reddit = praw.Reddit(user_agent=user_agent, client_id=client_id, client_secret=client_secret, username=username, password=pword)
    print("[bot] Posting {} - {} - to /r/{} (positivity = {})".format(str(post_title), str(post_url).encode("utf-8"), subreddit, score))
    post = reddit.subreddit(subreddit).submit(title=post_title, url=post_url)
    post.mod.flair(text="Positivity={}".format(score))
    log("[bot] Posting {} - {} - to /r/{} (positivity = {})".format(str(post_title).encode("ascii", "replace"), str(post_url), subreddit, score))
    time.sleep(1) # Reddit API limited to 60 requests per minute


def sentiment(link, title):
    # r = requests.post('http://text-processing.com/api/sentiment/', data = {'text': title})
    # posnegneutral = json.loads(r.text)['label']
    
    try:
        link_pos = indicoio.sentiment_hq(link)
        if link_pos > 0.9 or link_pos < 0.2:
            # save an API call 
            # - don't need to waste one if page contents already > 0.9 or < 0.2 (pos)
            title_pos = link_pos
        else:
            title_pos = indicoio.sentiment_hq(title)
        
        avg_pos = (link_pos + title_pos) / 2
        
        if link_pos > 0.9 or title_pos > 0.9:
            posnegneutral = "pos - {} (max)".format(max(link_pos, title_pos))
        elif avg_pos > 0.8:
            posnegneutral = "pos - {} (avg)".format(avg_pos)
        elif link_pos < 0.2 or title_pos < 0.2:
            posnegneutral = "neg - {} (min)".format(min(link_pos, title_pos))
        elif avg_pos < 0.3:
            posnegneutral = "neg - {} (avg)".format(avg_pos)
        else:
            posnegneutral = "neutral (link_pos={} title_pos={} avg={})".format(link_pos, title_pos, avg_pos)
            
    except:
        e = sys.exc_info()
        posnegneutral = "ERROR Checking Sentiment: {}".format(e)
        link_pos = 0
        title_pos = 0
        avg_pos = 0
    
    return posnegneutral, link_pos, title_pos, avg_pos


def duplicate_check_url(url):
    found = 0
    with open('posted_posts_urls.txt', 'r') as file:
        for line in file:
            if url in line:
                found = 1
    return found


def log(event):
    with open('log.txt', 'a') as file:
        file.write(str(event) + "\n")

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
