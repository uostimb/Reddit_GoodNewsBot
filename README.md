# Reddit GoodNewsBot

During a period of seemingly never-ending depressing news stories I decided to create a system that would  attempt to identify positive news stories and post them to a "JustGoodNews" sub on reddit.

This bot uses the popular PRAW Python Reddit API wrapper library and an API from Indicogo.IO 

Each time the bots runs it retrieves 1000 news posts from the subreddits "worldnews", "worldnews_uk", and "news", checks if it has seen the submitted news URLs before, then sends any new post titles and linked page URLs to a machine learning sentiment analysis service API hosted by Indico.IO.  News stories classed as Positive* are then reposted to reddit.com/r/JustGoodNews and Negative* news stories are reposted to reddit.com/r/JustBadNews.

To my eternal surprise and mild annoyance the /r/JustBadNews subreddit remains far more popular than /r/JustGoodNews.

*although Indicogo.IO's Machine Learning "High Quality Sentiment Analysis" accuracy is improving over time, at the time of writing it currently only classifies ~80% of news posts correctly.  
