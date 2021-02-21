from neo4j import GraphDatabase
from pprint import pprint
from collections import Counter

from tests import api_
from reddit_detective import RedditNetwork, Comments, CommentsReplies
from reddit_detective.data_models import Redditor, Submission

driver_ = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "test2")
)


def test_network_creation():
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


def test_code_uniqueness():
    obj = CommentsReplies(Submission(api_, "jpt7s7", limit=None))
    net = RedditNetwork(
        driver=driver_,
        components=[
            obj
        ]
    )
    obj_code_list = obj.code()
    net_code_list = list(net._codes())
    # if a submission's author has comments authored by themselves,
    # merges of each such person will be 2 in obj_code_list and 1 in net_code_list
    # that's why we do val <= 1
    # we'll avoid that extra merge too in the coming update
    assert all(
        val <= 1 for val in (Counter(obj_code_list) - Counter(net_code_list)).values()
    )


def run():
    test_code_uniqueness()
    # test_network_creation()


if __name__ == '__main__':
    run()
