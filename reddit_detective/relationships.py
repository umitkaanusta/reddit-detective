from typing import Union

from reddit_detective.data_models import Relationships
from reddit_detective.data_models import CommentData, Submission, Subreddit, Redditor

"""
Cypher code generation for relationships

Degree 1: Submissions
    Starting points: Subreddit OR Redditor
        Create nodes for all subreddits, submissions and redditors
        Link submissions to subreddits (UNDER)
        Link authors to submissions (AUTHORED)
"""


def _link_nodes(first_id, second_id, rel_type, props_str):
    """
    Using ids of two nodes and rel type, create code for linking nodes
    Why MATCHing first? Cause the following approach does not work:
        MERGE node1 with props p1
        MERGE node2 with props p2
        Creating relationship with node1 and node2 creates a relationship with nodes
        having the same type and props with node1 and node2. But node1 and node2 themselves
        won't be connected.
    """
    return """
MATCH (n1 {id: "%s"})
MATCH (n2 {id: "%s"})
WITH n1, n2
MERGE ((n1)-[:%s %s]->(n2));
    """ % (first_id, second_id, rel_type, props_str)


class Submissions:
    """
    Class to generate degree 1 code for Subreddit and Redditor objects
    """
    def __init__(self, starting_point: Union[Subreddit, Redditor]):
        if "submissions" not in starting_point.available_degrees:
            # if starting point is not Subreddit or Redditor:
            raise TypeError("the type of the starting point should be either Subreddit or Redditor")
        self.start = starting_point

    def _link_subs_to_subreddit(self):
        code_str = ""
        props = {}
        subs = self.start.submissions()
        for i in range(len(subs)):
            code_str += _link_nodes(
                subs[i].data["id"],
                subs[i].subreddit_id,
                Relationships.authored,
                props
            )
        return code_str

    def _link_subs_to_authors(self):
        code_str = ""
        props = {}
        subs = self.start.submissions()
        for i in range(len(subs)):
            code_str += _link_nodes(
                subs[i].author_id,
                subs[i].data["id"],
                Relationships.authored,
                props
            )
        return code_str

    def code(self):
        sr = self.start
        submissions = [sub.merge_code() for sub in sr.submissions()]
        authors = [sub.author.merge_code() for sub in sr.submissions()]
        code_str = f"{sr.merge_code()}\n" + "\n".join(submissions) + "\n" + "\n".join(authors) + ";"
        code_str += self._link_subs_to_subreddit()
        code_str += self._link_subs_to_authors()
        return code_str
