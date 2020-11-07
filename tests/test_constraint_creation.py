from neo4j import GraphDatabase

from reddit_detective import RedditNetwork

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
