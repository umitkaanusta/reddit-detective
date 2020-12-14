from reddit_detective.data_models import Redditor, Subreddit
from reddit_detective.relationships import Comments, CommentsReplies, Submissions
from tests import api_

"""
    Constraint codes to be run when manually testing in Neo4j:
    
    CREATE CONSTRAINT UniqueRedditor
        ON (r:Redditor) ASSERT (r.id) IS UNIQUE;
    
    CREATE CONSTRAINT UniqueSubmission
        ON (sm:Submission) ASSERT (sm.id) IS UNIQUE;
    
    CREATE CONSTRAINT UniqueSubreddit
        ON (sr:Subreddit) ASSERT (sr.id) IS UNIQUE;
    
    CREATE CONSTRAINT UniqueComment
        ON (c:Comment) ASSERT (c.id) IS UNIQUE;
"""


def test_submissions():
    red = Redditor(api_, "Anub_Rekhan", limit=2)
    submissions_red = Submissions(red)
    sub = Subreddit(api_, "learnpython", limit=2)
    submissions_sub = Submissions(sub)
    red_code = submissions_red.code()
    sub_code = submissions_sub.code()
    assert len(set(red_code)) == len(red_code)
    assert len(set(sub_code)) == len(sub_code)


def test_comments():
    red = Redditor(api_, "Anub_Rekhan", limit=2, indexing="new")
    comments_red = Comments(red)
    assert comments_red.comments()
    comm_code = comments_red.code()
    assert len(set(comm_code)) == len(comm_code)


def test_replies():
    sub = Subreddit(api_, "learnpython", limit=2, indexing="new")
    replies_sub = CommentsReplies(sub)
    assert replies_sub.comments()
    repl_code = replies_sub.code()
    assert len(set(repl_code)) == len(repl_code)


def run():
    test_submissions()
    test_comments()
    test_replies()


if __name__ == '__main__':
    run()
