from neo4j import GraphDatabase

from tests import api_
from reddit_detective import RedditNetwork, Submissions, Comments, CommentsReplies
from reddit_detective.data_models import Redditor, Subreddit, Submission

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testing")
)


def test_constraint_creation():
    net = RedditNetwork(
        driver=driver_,
        components=[]
    )
    net.create_constraints()


def run():
    test_constraint_creation()


if __name__ == '__main__':
    run()
