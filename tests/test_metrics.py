from neo4j import GraphDatabase

from reddit_detective.analytics.metrics import (interaction_score, interaction_score_normalized,
                                                cyborg_score_user, cyborg_score_submission,
                                                cyborg_score_subreddit)
from reddit_detective.analytics.utils import (get_redditors, get_user_comments_times,
                                              get_submission_comments_times, get_subreddit_comments_times)

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testing")
)


def test_get_users():
    users = get_redditors(driver_)
    assert users is not None
    assert isinstance(users, list)


def test_get_user_comments_times():
    # The test database should include some
    # comments/submissions of the test user
    ids, times = get_user_comments_times(driver_, "Anub_Rekhan")
    assert ids is not None
    assert isinstance(ids, list)
    assert times is not None
    assert isinstance(times, list)


def test_get_submission_comments_times():
    # The test database should include some
    # comments/submissions of the test submission
    ids, times = get_submission_comments_times(driver_, "hfulq4")
    assert ids is not None
    assert isinstance(ids, list)
    assert times is not None
    assert isinstance(times, list)


def test_get_subreddit_comments_times():
    # The test database should include some
    # comments/submissions of the test subreddit
    ids, times = get_subreddit_comments_times(driver_, "Python")
    assert ids is not None
    assert isinstance(ids, list)
    assert times is not None
    assert isinstance(times, list)


def test_interaction_score():
    sc = interaction_score(driver_, "Anub_Rekhan")
    assert sc is not None
    assert isinstance(sc, float)
    assert 0 <= sc <= 1


def test_interaction_score_normalized():
    sc = interaction_score_normalized(driver_, "Anub_Rekhan")
    assert sc is not None
    assert isinstance(sc, float)
    assert 0 <= sc <= 1


def test_cyborg_score_user():
    score, cyborgs = cyborg_score_user(driver_, "Anub_Rekhan")
    assert score is not None
    assert isinstance(score, float)
    assert 0 <= score <= 1
    assert cyborgs is not None
    assert isinstance(cyborgs, list)


def test_cyborg_score_submission():
    score, cyborgs = cyborg_score_submission(driver_, "hfulq4")
    assert score is not None
    assert isinstance(score, float)
    assert 0 <= score <= 1
    assert cyborgs is not None
    assert isinstance(cyborgs, list)


def test_cyborg_score_subreddit():
    score, cyborgs = cyborg_score_subreddit(driver_, "Python")
    assert score is not None
    assert isinstance(score, float)
    assert 0 <= score <= 1
    assert cyborgs is not None
    assert isinstance(cyborgs, list)


def run():
    test_get_users()
    test_get_user_comments_times()
    test_get_submission_comments_times()
    test_get_subreddit_comments_times()
    test_interaction_score()
    test_interaction_score_normalized()
    test_cyborg_score_user()
    test_cyborg_score_submission()
    test_cyborg_score_subreddit()


if __name__ == '__main__':
    run()
