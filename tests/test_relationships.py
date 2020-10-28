import praw

from reddit_detective.data_models import Redditor, Subreddit
from reddit_detective.relationships import Comments, Submissions
from tests import api_

"""
    Constraint codes to be run when testing in Neo4j:
    
    CREATE CONSTRAINT ExistsRedditor
    ON (r:Redditor) ASSERT (r.id) IS UNIQUE
    
    CREATE CONSTRAINT ExistsSubmission
    ON (sm:Submission) ASSERT (sm.id) IS UNIQUE
    
    CREATE CONSTRAINT ExistsSubreddit
    ON (sr:Subreddit) ASSERT (sr.id) IS UNIQUE
"""


def test_submissions():
    red = Redditor(api_, "Anub_Rekhan", limit=5)
    submissions_red = Submissions(red)
    sub = Subreddit(api_, "learnpython", limit=5)
    submissions_sub = Submissions(sub)
    # print(submissions_red.code())
    # print(submissions_sub.code())
    assert submissions_red.code()
    assert submissions_sub.code()


def test_comments():
    red = Redditor(api_, "Anub_Rekhan", limit=10, indexing="new")
    comments_red = Comments(red)
    assert comments_red.comments()
    assert comments_red.comment_authors()
    assert comments_red.comment_subs()
    assert comments_red._merge_nodes()
    assert comments_red.code()
    # print(comments_red.code())


def run():
    test_submissions()
    test_comments()
