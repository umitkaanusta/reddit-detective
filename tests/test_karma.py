from neo4j import GraphDatabase

from tests import api_
from reddit_detective import RedditNetwork, Submissions, Comments, CommentsReplies
from reddit_detective.data_models import Redditor, Subreddit, Submission

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testing")
)


def test_karma():
    net = RedditNetwork(
        driver=driver_,
        components=[]
    )
    net.add_karma(api_)


def run():
    test_karma()


if __name__ == '__main__':
    run()
