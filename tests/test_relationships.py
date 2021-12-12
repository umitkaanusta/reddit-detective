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
    sub = Subreddit.from_base_obj(api_.subreddit("learnpython"), 2)
    submissions_sub = Submissions(sub)
    assert submissions_sub.code()
    red = Redditor.from_base_obj(api_.redditor("Anub_Rekhan"), 2)
    submissions_red = Submissions(red)
    assert submissions_red.code()


def test_comments():
    sub = Subreddit.from_base_obj(api_.subreddit("learnpython"), 2)
    comments_sub = Comments(sub)
    assert comments_sub.comments()
    assert comments_sub.code()
    red = Redditor.from_base_obj(api_.redditor("Anub_Rekhan"), 2)
    comments_red = Comments(red)
    assert comments_red.comments()
    assert comments_red.code()


def test_replies():
    sub = Subreddit.from_base_obj(api_.subreddit("learnpython"), 2)
    replies_sub = CommentsReplies(sub)
    assert replies_sub.comments()
    assert replies_sub.code()
    red = Redditor.from_base_obj(api_.redditor("Anub_Rekhan"), 2)
    replies_red = CommentsReplies(red)
    assert replies_red.comments()
    assert replies_red.code()


def run():
    test_submissions()
    test_comments()
    test_replies()


if __name__ == '__main__':
    run()
