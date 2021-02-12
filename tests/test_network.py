from neo4j import GraphDatabase

from tests import api_
from reddit_detective import RedditNetwork, Comments
from reddit_detective.data_models import Redditor

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testing")
)


def test_network():
    net = RedditNetwork(
        driver=driver_,
        components=[
            Comments(Redditor(api_, "BloodMooseSquirrel", limit=5)),
            Comments(Redditor(api_, "Anub_Rekhan", limit=5))
        ]
    )
    assert net
    assert net.cypher_code()
    net.run_cypher_code()


def run():
    test_network()


if __name__ == '__main__':
    run()
