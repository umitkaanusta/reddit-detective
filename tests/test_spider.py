import praw
from neo4j import GraphDatabase
import pandas as pd

from reddit_detective import RedditNetwork, Comments, Submissions
from reddit_detective.data_models import Comment, Submission, Subreddit, Redditor
from reddit_detective.analytics import spider

search_subreddits = ['bioinformatics', 'genetics']
search_subreddits_comments = ['DNA', 'PhD','COVID']

# Create PRAW client instance
api = praw.Reddit(
    client_id="yourclientid",
    client_secret="yourclientsecret",
    password="password",
    user_agent="reddit-detective",
    username="username",    
)

# Create driver instance
driver = GraphDatabase.driver("bolt://localhost:7687",auth=("database_name", "database_password"))

reddit_users = spider.analyse_subreddits(api, search_subreddits, search_subreddits_comments)

comments= []
for name in list(set(reddit_users['author'])):
    com = Comments(Redditor(api, name, limit=5))
    comments.append(com)
    
net = RedditNetwork(driver=driver, components=comments)
##net.create_constraints()
net.run_cypher_code()

print('Finish.')