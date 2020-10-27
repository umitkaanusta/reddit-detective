import praw
from neo4j import GraphDatabase
from typing import List, Union

from reddit_detective.data_models import Redditor, Submission, Subreddit


class RedditNetwork:
    """
    This will be the outcome of conversion of Reddit data to a social network
    compatible with Neo4j.
    """
    def __init__(
            self,
            api: praw.Reddit,
            driver: GraphDatabase,
            starting_points: List[Union[Subreddit, Submission, Redditor]]
    ):
        self.api = api
        self.driver = driver
        self.starting_points = starting_points

    def cypher_code(self):
        """
        Creates CypherQL code to be run in Neo4j
        Use only this function if you want to just get the code but not run it
        """
        pass

    def run_cypher_code(self):
        """
        Runs the code created by self.cypher_code in your DB
        """
        pass
