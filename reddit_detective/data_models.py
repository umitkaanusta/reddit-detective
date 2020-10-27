import praw
from abc import ABC
from enum import Enum

from reddit_detective.utils import strip_punc

"""
Node types:
    Redditor
        Employee
        Mod
        Gold
    Submission
        Archived
        Stickied
        Locked
        Over18
    Subreddit
        Over18
        
Relationship types:
    MODERATES (Redditor -> Subreddit)
    UNDER (Submission -> Subreddit)
    COMMENTED (Redditor -> Submission)
    REPLIED (Redditor -> Redditor)
    AUTHORED (Redditor -> Submission)
    
Textual properties are stripped from punctuation marks to 
better comply with how Cypher deals with strings,
with a similar mindset with how Alexander solved the Gordian Knot.
"""

_ACCEPTED_INDEXES = ["hot", "new", "controversial", "top"]  # Do NOT alter this
_ACCEPTED_TIME_FILTERS = ["all", "hour", "day", "week", "month", "year"]  # Do NOT alter this


class CommentData:
    """
    Holds code generation methods and data of comments
    NOT A NODE, just a helper class to hold comment data
    """
    def __init__(self, api: praw.Reddit, id_):
        self.api = api
        self.id = id_
        self.resp = api.comment(id_)

    @property
    def properties(self):
        return {
            "id": self.resp.id,
            "edited": self.resp.edited,
            "text": strip_punc(self.resp.body),
            "is_submitter": self.resp.is_submitter,
            "score": self.resp.score,
            "stickied": self.resp.stickied
        }

    @property
    def author(self):
        username = self.resp.author.name
        return Redditor(self.api, username, limit=None)

    @property
    def submission(self):
        submission = self.resp.submission.id
        return Submission(self.api, submission, limit=None)

    @property
    def subreddit(self):
        subreddit = self.resp.subreddit.display_name
        return Subreddit(self.api, subreddit, limit=None)

    def replies(self):
        return list(self.resp.replies)


class Node(ABC):
    """
    Abstract class to implement common properties of nodes
    and methods for Cypher code generation

    self.data is the filtered version of the output we get from Reddit API
    self.properties are the properties we're gonna show at the Graph Database
    """
    def __init__(self, api: praw.Reddit, name, limit, indexing, time_filter, degree):
        if indexing not in _ACCEPTED_INDEXES:
            raise ValueError(f"reddit_detective only accepts {_ACCEPTED_INDEXES} as indexes")
        if time_filter not in _ACCEPTED_TIME_FILTERS:
            raise ValueError(f"reddit_detective only accepts {_ACCEPTED_TIME_FILTERS} as time filters")
        if degree not in self.available_degrees:
            raise ValueError(f"{self.main_type} only accepts {self.available_degrees} as degrees")
        self.api = api
        self.name = name
        self.limit = limit
        self.indexing = indexing
        self.time_filter = time_filter
        self.degree = degree

    @property
    def types(self):
        type_list = [self.main_type]
        for type_ in self.available_types:
            if self.data[type_.lower()]:
                type_list.append(type_)
        return type_list

    @property
    def properties(self):
        data = self.data
        for type_ in self.available_types:
            del data[type_.lower()]
        if "submissions" in data.keys():
            del data["submissions"]
        if "comments" in data.keys():
            del data["comments"]
        return data

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
        return f"({self.types_code()} {self.props_code()})"

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

    def __init__(self, api, name, limit, indexing="hot", time_filter="all", degree="comments"):
        super(Subreddit, self).__init__(api, name, limit, indexing, time_filter, degree)
        self.resp = self.api.subreddit(self.name)

    @property
    def data(self):
        return {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "name": self.resp.display_name,
            "over18": self.resp.over18,
            "desc": strip_punc(self.resp.description),
            "subscribers": self.resp.subscribers,
            "submissions": {
                "new": self.resp.new(limit=self.limit),
                "hot": self.resp.hot(limit=self.limit),
                "controversial": self.resp.controversial(time_filter=self.time_filter, limit=self.limit),
                "top": self.resp.top(time_filter=self.time_filter, limit=self.limit)
            }
        }

    def submissions(self):
        """
        Return the submissions as a list of data_models.Submission objects

        Assuming that the user would look for every comments in submissions if they're
        searching submissions under a subreddit, limit is set to None.
        (if not, they can fiddle with this at the Submission level)
        """
        subs = self.data["submissions"][self.indexing]
        ids = [sub.id for sub in subs]
        return [Submission(self.api, id_, limit=None) for id_ in ids]

    def __str__(self):
        return f"Subreddit({self.name})"


class Submission(Node):
    # https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
    main_type = "Submission"
    available_types = ["Archived", "Stickied", "Locked", "Over18"]
    available_degrees = ["comments", "replies"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all", degree="comments"):
        super(Submission, self).__init__(api, name, limit, indexing, time_filter, degree)
        self.resp = self.api.submission(self.name)

    @property
    def data(self):
        return {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "title": strip_punc(self.resp.title),
            "text": strip_punc(self.resp.selftext),
            "archived": self.resp.archived,
            "stickied": self.resp.stickied,
            "locked": self.resp.locked,
            "over18": self.resp.over_18,
            "score": self.resp.score,
            "upvote_ratio": self.resp.upvote_ratio,
            "edited": self.resp.edited
        }

    @property
    def author(self):
        username = self.resp.author.name
        return Redditor(self.api, username, limit=None)

    @property
    def subreddit(self):
        sub = self.resp.subreddit.id
        return Subreddit(self.api, sub, limit=None)

    def comments(self):
        """
        Returns the comments of the user as a list of CommentData objects
        """
        c = list(self.resp.comments)
        comments_data = [CommentData(self.api, comm.id) for comm in c]
        return comments_data

    def __str__(self):
        return f"Submission(id={self.name})"


class Redditor(Node):
    # https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html
    # Refer to https://praw.readthedocs.io/en/latest/code_overview/models/comment.html for comments
    main_type = "Redditor"
    available_types = ["Employee", "Mod", "Gold"]
    available_degrees = ["submissions", "comments", "replies"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all", degree="comments"):
        super(Redditor, self).__init__(api, name, limit, indexing, time_filter, degree)
        self.resp = self.api.redditor(self.name)

    @property
    def data(self):
        return {
            "id": self.resp.id,
            "username": self.resp.name,
            "created_utc": self.resp.created_utc,
            "has_verified_email": self.resp.has_verified_email,
            "comment_karma": self.resp.comment_karma,
            "link_karma": self.resp.link_karma,
            "employee": self.resp.is_employee,
            "mod": self.resp.is_mod,
            "gold": self.resp.is_gold,
            "submissions": {
                "new": self.resp.submissions.new(limit=self.limit),
                "hot": self.resp.submissions.hot(limit=self.limit),
                "controversial":
                    self.resp.submissions.controversial(time_filter=self.time_filter, limit=self.limit),
                "top": self.resp.submissions.top(time_filter=self.time_filter, limit=self.limit)
            },
            "comments": {
                "new": self.resp.comments.new(limit=self.limit),
                "hot": self.resp.comments.hot(limit=self.limit),
                "controversial":
                    self.resp.comments.controversial(time_filter=self.time_filter, limit=self.limit),
                "top": self.resp.comments.top(time_filter=self.time_filter, limit=self.limit)
            }
        }

    def submissions(self):
        """
        Return the submissions as a list of Submission objects

        Assuming that the user would look for every comments in submissions if they're
        searching submissions of a redditor, limit is set to None.
        (if not, they can fiddle with this at the Submission level)
        """
        subs = self.data["submissions"][self.indexing]
        ids = [sub.id for sub in subs]
        return [Submission(self.api, id_, limit=None) for id_ in ids]

    def comments(self):
        """
        Returns the comments of the user as a list of CommentData objects
        """
        c = list(self.data["comments"][self.indexing])
        comments_data = [CommentData(self.api, comm.id) for comm in c]
        return comments_data

    def __str__(self):
        return f"Redditor({self.name})"


class Relationships(Enum):
    moderates = "MODERATES",
    under = "UNDER",
    commented = "COMMENTED",
    authored = "AUTHORED",
    replied = "REPLIED"
