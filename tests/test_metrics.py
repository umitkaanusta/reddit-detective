from neo4j import GraphDatabase

from reddit_detective.analytics.metrics import interaction_score, interaction_score_normalized
from reddit_detective.analytics.utils import get_redditors

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testing")
)


def test_get_users():
    users = get_redditors(driver_)
    assert users is not None
    assert isinstance(users, list)


def test_interaction_score():
    # The test database should include some
    # comments/submissions of the test user
    sc = interaction_score(driver_, "Anub_Rekhan")
    assert sc is not None
    assert isinstance(sc, float)
    assert 0 <= sc <= 1


def test_interaction_score_normalized():
    sc = interaction_score_normalized(driver_, "Anub_Rekhan")
    assert sc is not None
    assert isinstance(sc, float)
    assert 0 <= sc <= 1


def run():
    test_get_users()
    test_interaction_score()
    test_interaction_score_normalized()


if __name__ == '__main__':
    run()
