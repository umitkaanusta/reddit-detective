import praw
from neo4j import BoltDriver
from typing import List, Union
from itertools import chain

from reddit_detective.relationships import Submissions, Comments, CommentsReplies
from reddit_detective.karma import (_remove_karma, _set_karma_subreddits, _set_karma_submissions,
                                    _set_karma_redditors, _set_karma_comments)


# Do not alter
_CONSTRAINTS = [
    """CREATE CONSTRAINT UniqueRedditor
        ON (r:Redditor) ASSERT (r.id) IS UNIQUE;""",
    
    """CREATE CONSTRAINT UniqueSubmission
        ON (sm:Submission) ASSERT (sm.id) IS UNIQUE;""",
    
    """CREATE CONSTRAINT UniqueSubreddit
        ON (sr:Subreddit) ASSERT (sr.id) IS UNIQUE;""",

    """CREATE CONSTRAINT UniqueComment
        ON (c:Comment) ASSERT (c.id) IS UNIQUE;"""
]


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

    def _run_query(self, codes):
        def run_code(tx):
            for query in codes:
                tx.run(query)
        with self.driver.session() as session:
            session.write_transaction(run_code)

    def _ids(self):
        """
        Get id of each node and relationship
        """
        d = self.driver
        s = d.session()
        subreddits_result = s.run("MATCH (n:Subreddit) RETURN n.name AS name")
        submissions_result = s.run("MATCH (n:Submission) RETURN n.id AS id")
        redditors_result = s.run("MATCH (n:Redditor) RETURN n.username AS name")
        comms_result = s.run("MATCH (c:Comment) RETURN c.id AS id")
        return [subreddits_result, submissions_result, redditors_result, comms_result]

    def add_karma(self, api: praw.Reddit):
        self.remove_karma()  # Clear karma at the beginning to comply with Constraints
        ids = self._ids()
        codes = _set_karma_subreddits(api, ids[0])
        codes += _set_karma_submissions(api, ids[1])
        codes += _set_karma_redditors(api, ids[2])
        codes += _set_karma_comments(api, ids[3])
        self._run_query(codes)

    def remove_karma(self):
        self._run_query(_remove_karma())

    def create_constraints(self):
        """
        Creates the needed constraints for the Network (optional but highly recommended)
        Make sure that the given constraints DON'T exist in your DB before calling the method.
        Otherwise Neo4j gives an error
        """
        self._run_query(codes=_CONSTRAINTS)

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
        self._run_query(codes=self._codes())
