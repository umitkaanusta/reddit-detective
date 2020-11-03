from typing import Union
from itertools import chain

from reddit_detective.data_models import Relationships
from reddit_detective.data_models import Comment, Submission, Subreddit, Redditor


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
    Degree 1: Submissions
    Starting points: Subreddit OR Redditor
        Create nodes for all subreddits, submissions and redditors
        Link submissions to subreddits (UNDER)
        Link authors to submissions (AUTHORED)
    """
    def __init__(self, starting_point: Union[Subreddit, Redditor]):
        if "submissions" not in starting_point.available_degrees:
            # if starting point is not Subreddit or Redditor:
            raise TypeError("the type of the starting point should be either Subreddit or Redditor")
        self.start = starting_point

    def _link_subs_to_subreddit(self, additional_subs=None):
        codes = []
        props = {}
        subs = self.start.submissions()
        if additional_subs:
            subs += additional_subs
        for i in range(len(subs)):
            codes.append(_link_nodes(
                subs[i].data["id"],
                subs[i].subreddit_id,
                Relationships.under,
                props
            ))
        return codes

    def _link_subs_to_authors(self, additional_subs=None):
        codes = []
        props = {}
        subs = self.start.submissions()
        if additional_subs:
            subs += additional_subs
        for i in range(len(subs)):
            codes.append(_link_nodes(
                subs[i].author_id,
                subs[i].data["id"],
                Relationships.authored,
                props
            ))
        return codes

    def _merge_nodes(self):
        start = self.start
        subreddits = list(set(Subreddit(start.api, sub.subreddit_name, limit=None).merge_code()
                      for sub in start.submissions()))
        submissions = list(set(sub.merge_code() for sub in start.submissions()))
        authors = list(set(sub.author.merge_code() for sub in start.submissions()))
        return subreddits + submissions + authors

    def code(self):
        code = self._merge_nodes()
        code += self._link_subs_to_subreddit()
        code += self._link_subs_to_authors()
        return code


class Comments(Submissions):
    """
    Degree 2: Comments
    Starting points: Subreddit, Submission, Redditor
        All of Degree 1
        Link redditors with subreddits via comments (COMMENTED)
    """
    def __init__(self, starting_point: Union[Subreddit, Submission, Redditor]):
        if "comments" not in starting_point.available_degrees:
            # if starting point is not Subreddit, Submission or Redditor:
            raise TypeError("the type of the starting point should be either "
                            "Subreddit, Submission or Redditor")
        self.start = starting_point

    def comments(self):
        # Return comments as a Python list
        if isinstance(self.start, Subreddit):
            subs = self.start.submissions()
            return list(chain.from_iterable([sub.comments() for sub in subs]))
        return self.start.comments()

    def comment_subs(self):
        return [Submission(self.start.api, comm.submission.id, limit=None)
                for comm in self.comments()]

    def comment_authors(self):
        return [Redditor(self.start.api, comm.author.name, limit=None)
                for comm in self.comments()]

    def _link_comments_to_subs(self):
        codes = []
        props = {}
        comments = self.comments()
        for i in range(len(comments)):
            codes.append(_link_nodes(
                comments[i].id,
                comments[i].submission.id,
                Relationships.under,
                props
            ))
        return codes

    def _link_authors_to_comms(self):
        codes = []
        props = {}
        comments = self.comments()
        for i in range(len(comments)):
            codes.append(_link_nodes(
                comments[i].author.id,
                comments[i].id,
                Relationships.authored,
                props
            ))
        return codes

    def _merge_nodes(self):
        start = self.start
        # Adding comments' submissions to start.submissions()
        submissions = list(set(sub.merge_code() for sub in
                       start.submissions() + self.comment_subs()))
        # Getting subreddits and their authors for every submission
        subreddits = list(set(Subreddit(start.api, sub.subreddit_name, limit=None).merge_code()
                      for sub in start.submissions() + self.comment_subs()))
        comments = list(set(Comment(start.api, comm.id).merge_code()
                            for comm in self.comments()))
        authors = [sub.author.merge_code() for sub in start.submissions()]
        authors += [sub.author.merge_code() for sub in self.comment_subs()]
        authors = list(set(authors))
        # Adding commentor users
        commentors = list(set(auth.merge_code() for auth in self.comment_authors()))
        return subreddits + submissions + authors + commentors + comments

    def code(self):
        code = self._merge_nodes()
        code += self._link_subs_to_subreddit(additional_subs=self.comment_subs())
        code += self._link_subs_to_authors(additional_subs=self.comment_subs())
        code += self._link_comments_to_subs()
        code += self._link_authors_to_comms()
        return code


class CommentsReplies(Comments):
    """
    Note that CommentsReplies has a higher time complexity
    
    Degree 3: Replies
    Starting points: Subreddit, Submission, Redditor
        All of Degree 2
        For all comments, get the list of replies
        Link redditors to redditors thru which one replied to other (REPLIED)
    """
    def __init__(self, starting_point: Union[Subreddit, Submission, Redditor]):
        if "replies" not in starting_point.available_degrees:
            # if starting point is not Subreddit, Submission or Redditor:
            raise TypeError("the type of the starting point should be either "
                            "Subreddit, Submission or Redditor")
        self.start = starting_point

    def _link_replies_to_comms(self):
        codes = []
        props = {}
        comments = self.comments()
        for i in range(len(comments)):
            replies = comments[i].replies
            for j in range(len(replies)):
                codes.append(_link_nodes(
                    comments[i].id,
                    replies[j].id,
                    Relationships.under,
                    props
                ))
        return codes

    def code(self):
        code = super().code()
        code += self._link_replies_to_comms()
        return code
