import praw

from reddit_detective.data_models import Subreddit
from reddit_detective.relationships import Submissions
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
    sub = Subreddit(api_, "learnpython", limit=5, degree="submissions")
    submissions = Submissions(sub)
    code = Submissions(sub).code()
    assert "MERGE" in code
    assert "WITH" in code
    assert submissions._link_subs_to_subreddit() in code
    assert submissions._link_subs_to_authors() in code


def run():
    test_submissions()
