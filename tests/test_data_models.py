from reddit_detective.data_models import Comment, Submission, Subreddit, Redditor
from tests import api_

"""
Testing the basic properties/methods of data models and abstract classes
"""


def test_subreddit():
    sub = Subreddit.from_base_obj(api_.subreddit("learnpython"), limit=100)
    assert sub.main_type in sub.types
    assert sub.properties["created_utc"]
    assert sub.submissions() is not None
    assert sub.subscribers is not None  # it might be zero, 0 gives AssertionError


def test_submission():
    sub = Submission.from_base_obj(api_.submission("jhd0px"), limit=100)
    assert sub.main_type in sub.types
    assert sub.properties["created_utc"]
    assert isinstance(sub.subreddit, Subreddit)
    assert sub.comments() is not None
    assert sub.score is not None
    assert sub.upvote_ratio is not None
    assert sub.author_accessible, "Submission has no accessible author."
    assert isinstance(sub.author, Redditor)


def test_redditor():
    red = Redditor.from_base_obj(api_.redditor("Anub_Rekhan"), limit=100)
    assert red.properties["created_utc"]
    assert red.main_type in red.types
    assert red.properties["created_utc"]
    assert red.submissions() is not None
    assert red.comments() is not None
    assert red.link_karma is not None
    assert red.comment_karma is not None
    red_susp = Redditor.from_base_obj(api_.redditor("deleted"), limit=100)
    assert "Suspended" in red_susp.types
    assert red_susp.comments() == []
    assert red_susp.submissions() == []


def test_comment():
    cd = Comment.from_base_obj(api_.comment("gcltb0o"))
    assert cd.properties["text"]
    assert isinstance(cd.submission, Submission)
    assert cd.replies() is not None
    assert cd.score is not None
    assert cd.author_accessible, "Comment has no accessible author."
    assert isinstance(cd.author, Redditor)
    cd_by_deleted = Comment.from_base_obj(api_.comment("fo2ap22"))
    assert not cd_by_deleted.author_accessible


def test_cypher_codes_node():
    sub = Subreddit.from_base_obj(api_.subreddit("learnpython"), limit=100)
    assert sub.types_code()
    assert sub.types[0] in sub.types_code()
    assert ":" in sub.types_code()
    assert sub.props_code()
    assert sub.properties["id"] in sub.props_code()
    assert ":" in sub.props_code()
    assert "{" in sub.props_code() and "}" in sub.props_code()
    assert sub.merge_code()
    assert "MERGE" in sub.merge_code()
    assert sub.types_code() in sub.merge_code()
    assert sub.props_code() in sub.merge_code()


def run():
    test_subreddit()
    test_submission()
    test_redditor()
    test_comment()
    test_cypher_codes_node()


if __name__ == '__main__':
    run()
