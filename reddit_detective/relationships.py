from typing import Union
from itertools import chain

from reddit_detective.data_models import Relationships
from reddit_detective.data_models import Comment, Submission, Subreddit, Redditor
from praw.models import MoreComments


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


def _search_submission(comment, api):
    comment_list = [comment]
    _comment = comment
    while _comment.parent_id[3:] != _comment.submission.id:
        _comment = api.comment(_comment.parent_id[3:])
        comment_list.append(_comment)
    return comment_list


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

    def _merge_and_link_submissions(self, submission_list):
        submissions = []
        subreddits = []
        subreddit_links = []
        authors = []
        author_links = []
        props = {}

        unique_subs = {sub.data["id"]: sub for sub in submission_list}.values()

        for sub in unique_subs:
            submissions.append(sub.merge_code())

            subreddit_code = Subreddit(self.start.api, sub.subreddit_name, limit=None).merge_code()
            if subreddit_code not in subreddits:
                subreddits.append(subreddit_code)
            
            if sub.author_accessible:
                author_code = sub.author.merge_code()
                if author_code not in authors:
                    authors.append(author_code)

                author_links.append(_link_nodes(
                    sub.author_id,
                    sub.data["id"],
                    Relationships.authored,
                    props
                ))

            subreddit_links.append(_link_nodes(
                sub.data["id"],
                sub.subreddit_id,
                Relationships.under,
                props
            ))
        
        return subreddits + submissions + authors, subreddit_links + author_links

    def code(self):
        merges, links = self._merge_and_link_submissions(self.start.submissions())
        return merges + links


class Comments(Submissions):
    """
    Degree 2: Comments
    Starting points: Subreddit, Submission, Redditor
        All of Degree 1
        Link redditors with submissions via comments (AUTHORED)
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
        elif isinstance(self.start, Redditor):
            comment_list = []
            for comment in self.start.comments():
                comment_list = comment_list + _search_submission(comment, self.start.api)
            return comment_list
        else:
            return self.start.comments()

    def _merge_and_link_comments(self, comment_list):
        comment_codes = []
        parent_links = []
        submissions = []
        authors = []
        author_links = []
        props = {}
        for comment in comment_list:
            comment_instance = Comment(self.start.api, comment.id)
            comment_codes.append(comment_instance.merge_code())

            if comment_instance.author_accessible:
                author_code = comment_instance.author.merge_code()
                if author_code not in authors:
                    authors.append(author_code)
                
                author_links.append(_link_nodes(
                    comment_instance.author_id,
                    comment.id,
                    Relationships.authored,
                    props
                ))
            
            parent_links.append(_link_nodes(
                comment.id,
                comment.parent_id[3:],
                Relationships.under,
                props
            ))

            sub = Submission(self.start.api, comment.submission.id, limit=None)
            if sub not in submissions:
                submissions.append(sub)
        
        return comment_codes + authors, parent_links + author_links, submissions
    
    def code(self):
        comment_merges, comment_links, submissions = self._merge_and_link_comments(self.comments())
        sub_merges, sub_links = self._merge_and_link_submissions(submissions)
        return comment_merges + sub_merges + comment_links + sub_links


class CommentsReplies(Comments):
    """
    Note that CommentsReplies has a higher time complexity
    
    Degree 3: Replies
    Starting points: Subreddit, Submission, Redditor
        All of Degree 2
        For all comments, get the list of replies
        Link comments to replies (which are also comments) with UNDER relationship
    """
    def __init__(self, starting_point: Union[Subreddit, Submission, Redditor]):
        if "replies" not in starting_point.available_degrees:
            # if starting point is not Subreddit, Submission or Redditor:
            raise TypeError("the type of the starting point should be either "
                            "Subreddit, Submission or Redditor")
        self.start = starting_point

    def comments(self):
        # Return comments as a Python list
        if isinstance(self.start, Subreddit):
            subs = self.start.submissions()
            base_comment_list = list(chain.from_iterable([sub.comments() for sub in subs]))
            full_comment_list = base_comment_list
        elif isinstance(self.start, Redditor):
            full_comment_list = []
            comments = self.start.comments()
            for comment in comments:
                full_comment_list = full_comment_list + _search_submission(comment, self.start.api)
            # We are interested in the replies of submissions too
            subs = self.start.submissions()
            sub_comments = list(chain.from_iterable([sub.comments() for sub in subs]))
            base_comment_list = comments + sub_comments
            full_comment_list = full_comment_list + base_comment_list
        else:
            base_comment_list = self.start.comments()
            full_comment_list = base_comment_list
        for comment in base_comment_list:
            if isinstance(comment, MoreComments):
                base_comment_list += comment.comments()
                continue
            comment.refresh()
            for reply in comment.replies:
                full_comment_list.append(reply)
        return full_comment_list
