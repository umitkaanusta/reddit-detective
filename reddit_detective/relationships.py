from typing import Union
from itertools import chain
from typing import List

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


def _search_submission(comment):
    comment_list = [comment]
    curr = comment
    while curr.parent_id[:3] != "t3_":  # if the comment is not a top level comment:
        curr = curr.parent
        comment_list.append(curr)
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

    def _merge_and_link_submissions(self, submission_list: List[Submission]):
        submissions = []
        subreddits = []
        subreddit_links = []
        authors = []
        author_links = []
        props = {}

        unique_subs = {sub.properties["id"]: sub for sub in submission_list}.values()

        for sub in unique_subs:
            submissions.append(sub.merge_code())

            subreddit_code = sub.subreddit.merge_code()
            if subreddit_code not in subreddits:
                subreddits.append(subreddit_code)
            
            if sub.author_accessible:
                author_code = sub.author.merge_code()
                if author_code not in authors:
                    authors.append(author_code)

                author_links.append(_link_nodes(
                    sub.author_id,
                    sub.properties["id"],
                    Relationships.authored,
                    props
                ))

            subreddit_links.append(_link_nodes(
                sub.properties["id"],
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
        else:
            return self.start.comments()

    def _merge_and_link_comments(self, comment_list: List[Comment]):
        comment_codes = []
        parent_links = []
        submissions = []
        submission_ids = {}
        author_codes = []
        author_ids = {}
        author_links = []
        props = {}

        for comment in comment_list:
            comment_codes.append(comment.merge_code())

            if comment.author_accessible:
                if comment.author_id not in author_ids:
                    author_ids[comment.author_id] = True
                    author_codes.append(comment.author.merge_code())
                
                author_links.append(_link_nodes(
                    comment.author_id,
                    comment.properties["id"],
                    Relationships.authored,
                    props
                ))
            
            parent_links.append(_link_nodes(
                comment.properties["id"],
                comment.submission_id,
                Relationships.under,
                props
            ))

            if comment.submission_id not in submission_ids:
                submission_ids[comment.submission_id] = True
                submissions.append(comment.submission)
        
        return comment_codes + author_codes, parent_links + author_links, submissions
    
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
                full_comment_list = full_comment_list + _search_submission(comment)
            # We are interested in the replies of submissions too
            subs = self.start.submissions()
            sub_comments = list(chain.from_iterable([sub.comments() for sub in subs]))
            base_comment_list = comments + sub_comments
            full_comment_list = full_comment_list + base_comment_list
            full_comment_list = list(set(full_comment_list))
        else:
            base_comment_list = self.start.comments()
            full_comment_list = base_comment_list
        for comment in base_comment_list:
            if isinstance(comment, MoreComments):
                base_comment_list += comment.comments()
                continue
            try:
                comment.refresh()
                for reply in comment.replies:
                    full_comment_list.append(reply)
            except AttributeError:
                for reply in comment.replies():
                    full_comment_list.append(reply)
        return full_comment_list

    def _merge_and_link_comments(self, comment_list: List[Comment]):
        # to reduce duplication
        # and doing it this way performs better than
        # directly using the inherited method instead of overriding (?)
        return super()._merge_and_link_comments(comment_list)

    def code(self):
        comment_merges, comment_links, submissions = self._merge_and_link_comments(self.comments())
        sub_merges, sub_links = self._merge_and_link_submissions(submissions)
        return comment_merges + sub_merges + comment_links + sub_links
