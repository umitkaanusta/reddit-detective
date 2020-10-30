from neo4j import BoltDriver
from typing import List, Union
from itertools import chain

from reddit_detective.relationships import Submissions, Comments, CommentsReplies


class RedditNetwork:
    """
    This will be the outcome of conversion of Reddit data to a social network
    compatible with Neo4j.
    """
    def __init__(
            self,
            driver: BoltDriver,
            components: List[Union[Submissions, Comments, CommentsReplies]]
    ):
        self.driver = driver
        self.components = components

    def _codes(self):
        """
        Get codes for every component
        """
        codes = list(chain.from_iterable([point.code() for point in self.components]))
        # Remove duplicates without changing order
        codes = sorted(set(codes), key=lambda x: codes.index(x))
        return codes

    def cypher_code(self):
        """
        Use this function only if you want to just get the code but not run it
        """
        return "\n".join(self._codes())

    def run_cypher_code(self):
        def run_code(tx):
            for query in self._codes():
                tx.run(query)
            pass
        with self.driver.session() as session:
            session.write_transaction(run_code)
