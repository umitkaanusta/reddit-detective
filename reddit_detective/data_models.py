import praw
from prawcore.exceptions import Redirect, NotFound
from praw.models import (Comment as PrawComment,
                         Submission as PrawSubmission,
                         Subreddit as PrawSubreddit,
                         Redditor as PrawRedditor)
from abc import ABC
from typing import Union

from reddit_detective.utils import strip_punc

"""
Node types:
    Redditor
        Employee
        Suspended
    Submission
        Archived
        Stickied
        Locked
        Over18
    Subreddit
        Over18
    Comment
        
Relationship types:
    MODERATES (Redditor -> Subreddit) (No properties)
    UNDER (Submission -> Subreddit) OR (Submission -> Comment) OR (Comment -> Comment) (No properties)
    AUTHORED (Redditor -> Submission) OR (Redditor -> Comment) (No properties)
    
Textual properties are stripped from some certain punctuation marks 
to better comply with how Cypher deals with strings,
with a similar mindset with how Alexander solved the Gordian Knot.
"""

_ACCEPTED_INDEXES = ["hot", "new", "controversial", "top"]  # Do NOT alter this
_ACCEPTED_TIME_FILTERS = ["all", "hour", "day", "week", "month", "year"]  # Do NOT alter this


class Node(ABC):
    """
    Abstract class to implement common properties of nodes
    and methods for Cypher code generation

    self.properties are the properties we're gonna show at the Graph Database
    """
    def __init__(self,
                 api: Union[praw.Reddit, None],
                 name,
                 limit,
                 indexing,
                 time_filter,
                 base_obj: Union[PrawComment, PrawSubmission, PrawSubreddit, PrawRedditor] = None
                 ):
        if indexing not in _ACCEPTED_INDEXES:
            raise ValueError(f"reddit_detective only accepts {_ACCEPTED_INDEXES} as indexes")
        if time_filter not in _ACCEPTED_TIME_FILTERS:
            raise ValueError(f"reddit_detective only accepts {_ACCEPTED_TIME_FILTERS} as time filters")
        self.api = api
        self.name = name
        self.limit = limit
        self.indexing = indexing
        self.time_filter = time_filter
        self.base_obj = base_obj

    @classmethod
    def _from_base_obj(cls, base_obj, limit, indexing, time_filter):
        return cls(None, None, limit, indexing, time_filter, base_obj)

    @property
    def types(self):
        type_list = [self.main_type]
        for type_ in self.available_types:
            if self.properties[type_.lower()] == "True":
                # Boolean values are converted to str cause
                # Sometimes some data returns None but Neo4j does not recognize None as a type
                type_list.append(type_)
        return type_list

    def types_code(self):
        """
        Convert method self.types to Cypher code
        Example:
        Single type (Subreddit) -> :Subreddit
        Multi types (Redditor, Employee, Gold) -> :Redditor:Gold:Employee
        """
        return f":{':'.join(self.types)}"

    def props_code(self):
        """
        Convert method self.properties to Cypher code
        Example:
        {"title": "cat"} -> {title: 'cat'}
        {"comment_karma": 1, "username": "x"} -> {comment_karma: 1, username: 'x'}
        """
        keys, values = zip(*self.properties.items())
        props_str = ""
        for i in range(len(keys)):
            value_ = f"\"{values[i]}\"" if type(values[i]) == str else values[i]
            # Replace \n with two spaces
            prop = f"{keys[i]}: " + str(value_).replace("\n", "  ") + ","
            props_str += prop + " "
        return "{" + props_str[:-2] + "}"  # Delete the comma and space at the end with [:-2]

    def code(self):
        """
        Denotes a node, to be used in defining relationships etc.
        """
        return f"({self.types_code()} {self.props_code()});"

    def merge_code(self):
        """
        We use MERGE instead of CREATE, so that a duplicate node
        should not be created in case the node exists.
        """
        return "MERGE " + self.code()


class Subreddit(Node):
    # https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html
    main_type = "Subreddit"
    available_types = ["Over18"]
    available_degrees = ["submissions", "comments", "replies"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all", base_obj=None):
        super(Subreddit, self).__init__(api, name, limit, indexing, time_filter, base_obj)
        self.resp = base_obj if base_obj else self.api.subreddit(self.name)
        # Making "resp" an attribute to reach stuff outside
        # self.properties and self._submissions_cached if needed
        self.properties = {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "name": str(self.resp.display_name),
            "over18": str(self.resp.over18),
            "desc": str(strip_punc(self.resp.description))
        }
        self._submissions_cached = {}

    @classmethod
    def from_base_obj(cls, base_obj, limit, indexing="hot", time_filter="all"):
        return cls._from_base_obj(base_obj, limit, indexing, time_filter)

    @property
    def subscribers(self):
        return self.resp.subscribers

    def submissions(self):
        """
        Return the submissions as a list of data_models.Submission objects

        Assuming that the user would look for every comments in submissions if they're
        searching submissions under a subreddit, limit is set to None.
        (if not, they can fiddle with this at the Submission level)
        """
        if not self._submissions_cached:
            self._submissions_cached = {
                "new": list(self.resp.new(limit=self.limit)),
                "hot": list(self.resp.hot(limit=self.limit)),
                "controversial": list(
                    self.resp.controversial(time_filter=self.time_filter, limit=self.limit)
                ),
                "top": list(self.resp.top(time_filter=self.time_filter, limit=self.limit))
            }
        subs = self._submissions_cached[self.indexing]
        return [Submission.from_base_obj(sub, limit=None) for sub in subs]

    def __str__(self):
        return f"Subreddit({self.properties['name']})"


class SubOrComment(Node):
    @property
    def author_accessible(self):
        return self.resp.author is not None
    
    @property
    def author(self):
        return Redditor.from_base_obj(self.resp.author, limit=None)

    @property
    def author_id(self):
        try:
            return self.resp.author.id
        except AttributeError:
            return self.resp.author.name
    
    @property
    def score(self):
        return self.resp.score


class Submission(SubOrComment):
    # https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
    main_type = "Submission"
    available_types = ["Archived", "Stickied", "Locked", "Over18"]
    available_degrees = ["comments", "replies"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all", base_obj=None):
        super(Submission, self).__init__(api, name, limit, indexing, time_filter, base_obj)
        self.resp = base_obj if base_obj else self.api.submission(self.name)
        self.properties = {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "title": str(strip_punc(self.resp.title)),
            "text": str(strip_punc(self.resp.selftext)),
            "archived": str(self.resp.archived),
            "stickied": str(self.resp.stickied),
            "locked": str(self.resp.locked),
            "over18": str(self.resp.over_18),
        }
        self._comments_cached = []

    @classmethod
    def from_base_obj(cls, base_obj, limit, indexing="hot", time_filter="all"):
        return cls._from_base_obj(base_obj, limit, indexing, time_filter)

    @property
    def upvote_ratio(self):
        return self.resp.upvote_ratio

    @property
    def subreddit(self):
        return Subreddit.from_base_obj(self.resp.subreddit, limit=None)

    @property
    def subreddit_id(self):
        return self.resp.subreddit.id

    @property
    def subreddit_name(self):
        return self.resp.subreddit.display_name

    def comments(self):
        if not self._comments_cached:
            self._comments_cached = list(self.resp.comments)
        lim = self.limit if self.limit is not None else len(self._comments_cached)
        return [Comment.from_base_obj(comm) for comm in self._comments_cached[:lim]]

    def __str__(self):
        return f"Submission(id={self.properties['id']})"


class Redditor(Node):
    # https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html
    main_type = "Redditor"
    available_types = ["Employee", "Suspended"]
    available_degrees = ["submissions", "comments", "replies"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all", base_obj=None):
        super(Redditor, self).__init__(api, name, limit, indexing, time_filter, base_obj)
        self.resp = base_obj if base_obj else self.api.redditor(self.name)
        self._submissions_cached = {}
        self._comments_cached = {}
        try:
            _ = self.resp.created_utc
            self.properties = {
                "id": self.resp.id,
                "username": str(self.resp.name),
                "created_utc": self.resp.created_utc,
                "has_verified_email": str(self.resp.has_verified_email),
                "employee": str(self.resp.is_employee),
                "suspended": "False"
            }
        except AttributeError:
            self.properties = {
                "id": str(self.resp.name),
                "username": str(self.resp.name),
                "suspended": "True",
                "employee": "False"
            }

    @classmethod
    def from_base_obj(cls, base_obj, limit, indexing="hot", time_filter="all"):
        return cls._from_base_obj(base_obj, limit, indexing, time_filter)

    @property
    def comment_karma(self):
        return self.resp.comment_karma

    @property
    def link_karma(self):
        return self.resp.link_karma

    def submissions(self):
        """
        Return the submissions as a list of Submission objects

        Assuming that the user would look for every comments in submissions if they're
        searching submissions of a redditor, limit is set to None.
        (if not, they can fiddle with this at the Submission level)
        """
        if self.properties["suspended"] == "True":
            return []
        if not self._submissions_cached:
            self._submissions_cached = {
                "new": list(self.resp.submissions.new(limit=self.limit)),
                "hot": list(self.resp.submissions.hot(limit=self.limit)),
                "controversial": list(
                    self.resp.submissions.controversial(time_filter=self.time_filter, limit=self.limit)
                ),
                "top": list(self.resp.submissions.top(time_filter=self.time_filter, limit=self.limit))
            }
        subs = self._submissions_cached[self.indexing]
        return [Submission.from_base_obj(sub, limit=None) for sub in subs]

    def comments(self):
        if self.properties["suspended"] == "True":
            return []
        if not self._comments_cached:
            self._comments_cached = {
                "new": list(self.resp.comments.new(limit=self.limit)),
                "hot": list(self.resp.comments.hot(limit=self.limit)),
                "controversial": list(
                    self.resp.comments.controversial(time_filter=self.time_filter, limit=self.limit)
                ),
                "top": list(self.resp.comments.top(time_filter=self.time_filter, limit=self.limit))
            }
        comms = self._comments_cached[self.indexing]
        return [Comment.from_base_obj(comm) for comm in comms]

    def __str__(self):
        return f"Redditor({self.properties['username']})"


class Comment(SubOrComment):
    # https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
    main_type = "Comment"
    available_types = []

    def __init__(self, api: Union[praw.Reddit, None], id_, base_obj=None):
        self.api = api
        self.id = id_
        self.base_obj = base_obj
        self.resp = base_obj if base_obj else api.comment(id_)
        self.properties = {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "text": strip_punc(self.resp.body),
            "is_submitter": str(self.resp.is_submitter),
            "stickied": str(self.resp.stickied)
        }

    @classmethod
    def from_base_obj(cls, base_obj):
        return cls(None, None, base_obj)

    @property
    def parent(self):
        if self.parent_id[:3] == "t3_":
            return self.submission
        return Comment.from_base_obj(self.resp.parent())

    @property
    def parent_id(self):
        return self.resp.parent_id

    @property
    def submission(self):
        return Submission.from_base_obj(self.resp.submission, limit=None)

    @property
    def submission_id(self):
        return self.resp.submission.id

    def replies(self):
        return [Comment.from_base_obj(comm) for comm in list(self.resp.replies)]

    def __str__(self):
        return f"Comment(id={self.properties['id']})"


class Relationships:
    moderates = "MODERATES"
    under = "UNDER"
    authored = "AUTHORED"
