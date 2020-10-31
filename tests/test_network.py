from neo4j import GraphDatabase

from tests import api_
from reddit_detective import RedditNetwork, Submissions, Comments, CommentsReplies
from reddit_detective.data_models import Redditor, Subreddit, Submission

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testing")
)


def test_network():
    net = RedditNetwork(
        driver=driver_,
        components=[
            Submissions(Redditor(api_, "yigitaga32", limit=2)),
            Comments(Redditor(api_, "Anub_Rekhan", limit=2))
        ]
    )
    assert net
    assert net.cypher_code()
    net.run_cypher_code()


def run():
    test_network()
