import praw

from reddit_detective.data_models import Redditor, Subreddit
from reddit_detective.relationships import Comments, CommentsReplies, Submissions
from tests import api_

"""
    Constraint codes to be run when manually testing in Neo4j:
    
    CREATE CONSTRAINT UniqueRedditor
    ON (r:Redditor) ASSERT (r.id) IS UNIQUE
    
    CREATE CONSTRAINT UniqueSubmission
    ON (sm:Submission) ASSERT (sm.id) IS UNIQUE
    
    CREATE CONSTRAINT UniqueSubreddit
    ON (sr:Subreddit) ASSERT (sr.id) IS UNIQUE
"""


def test_submissions():
    red = Redditor(api_, "Anub_Rekhan", limit=2)
    submissions_red = Submissions(red)
    sub = Subreddit(api_, "learnpython", limit=2)
    submissions_sub = Submissions(sub)
    # print(submissions_red.code())
    # print(submissions_sub.code())
    assert submissions_red.code()
    assert submissions_sub.code()


def test_comments():
    red = Redditor(api_, "Anub_Rekhan", limit=2, indexing="new")
    comments_red = Comments(red)
    assert comments_red.comments()
    assert comments_red.comment_authors()
    assert comments_red.comment_subs()
    assert comments_red.code()
    print(comments_red.code())


def test_replies():
    sub = Subreddit(api_, "learnpython", limit=2, indexing="hot")
    replies_sub = CommentsReplies(sub)
    assert replies_sub.code()


def run():
    test_submissions()
    test_comments()
    test_replies()


if __name__ == '__main__':
    run()
