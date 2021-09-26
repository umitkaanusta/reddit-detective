import praw
import pandas as pd
import datetime

from reddit_detective import RedditNetwork, Comments
from reddit_detective.data_models import Comment, Submission, Subreddit, Redditor
from reddit_detective.analytics import metrics

def analyse_subreddits(reddit, subreddits_wordlist, search_subreddits_comments):
    data = []
    print('Starting to gather data... (this operation can take a while)')
    for subreddit in subreddits_wordlist:
        subreddit_data = reddit.subreddit(subreddit)
        for submission in subreddit_data.new(limit=50):
            for top_level_comment in submission.comments:
                data.append([submission.id, subreddit, submission.author, datetime.datetime.fromtimestamp(submission.created), submission.name, submission.num_comments, submission.score, submission.title, submission.upvote_ratio, top_level_comment.body])
    data = pd.DataFrame(data, columns=['id', 'subreddit', 'author', 'created_date', 'name', 'num_comments', 'score', 'title', 'upvote_ratio', 'body']).drop_duplicates(subset=['id'], keep="last")
    print('Dataset gather filled.')

    print('Analysing data...')    
    dataset = data[data['body'].str.contains("|".join(search_subreddits_comments))]
    print('Extracted subreddit comments based on keywords:' + str(search_subreddits_comments))

    print('Creating graph structure... (this operation can take a while)')
    return pd.DataFrame(dataset)