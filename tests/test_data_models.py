import praw
from pprint import pprint

from reddit_detective.data_models import Submission, Subreddit, Redditor
from tests import api_


def test_subreddit():
    sub = Subreddit(api_, "learnpython", limit=100, indexing="hot", time_filter="all")
    assert sub
    assert sub.data["created_utc"]
    assert sub.types
    assert sub.properties
    assert sub.properties["created_utc"]
    assert sub.submissions() is not None


def test_submission():
    sub = Submission(api_, "jhd0px", limit=100, indexing="hot", time_filter="all")
    assert sub
    assert sub.data["created_utc"]
    assert sub.types
    assert sub.properties
    assert sub.properties["created_utc"]
    assert sub.author
    assert isinstance(sub.author, Redditor)
    assert sub.comments() is not None


def test_redditor():
    red = Redditor(api_, "Anub_Rekhan", limit=100, indexing="hot", time_filter="all")
    assert red
    assert red.data["created_utc"]
    assert red.types
    assert red.properties
    assert red.properties["created_utc"]
    assert red.comments() is not None
    print(list(red.comments()))


def test_cypher_codes_node():
    sub = Subreddit(api_, "learnpython", limit=100, indexing="hot", time_filter="all")
    assert sub.types_code()
    assert sub.types[0] in sub.types_code()
    assert ":" in sub.types_code()
    assert sub.props_code()
    assert sub.properties["id"] in sub.props_code()
    assert ":" in sub.props_code()
    assert "{" in sub.props_code() and "}" in sub.props_code()
    assert sub.merge_node_code()
    assert "MERGE" in sub.merge_node_code()
    assert sub.types_code() in sub.merge_node_code()
    assert sub.props_code() in sub.merge_node_code()


if __name__ == '__main__':
    test_subreddit()
    test_submission()
    test_redditor()
    test_cypher_codes_node()
