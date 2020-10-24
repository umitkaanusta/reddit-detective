import praw
from abc import ABC

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
    MODERATES (Redditor -> Subreddit):
    UNDER (Submission -> Subreddit):
    COMMENTED (Redditor -> Submission):
    REPLIED (Redditor -> Redditor):
    AUTHORED (Redditor -> Submission):
"""

_ACCEPTED_INDEXES = ["hot", "new", "controversial", "top"]  # Do NOT alter this
_ACCEPTED_TIME_FILTERS = ["all", "hour", "day", "week", "month", "year"]  # Do NOT alter this


class Node(ABC):
    """
    Abstract class to implement common properties of nodes
    and methods for Cypher code generation

    self.data is the filtered version of the output we get from Reddit API
    self.properties are the properties we're gonna show at the Graph Database
    """
    def __init__(self, api: praw.Reddit, name, limit, indexing="hot", time_filter="all"):
        if indexing not in _ACCEPTED_INDEXES:
            raise ValueError(f"reddit_detective only accepts {_ACCEPTED_INDEXES} as indexes")
        if time_filter not in _ACCEPTED_TIME_FILTERS:
            raise ValueError(f"reddit_detective only accepts {_ACCEPTED_TIME_FILTERS} as time filters")
        self.api = api
        self.name = name
        self.limit = limit
        self.indexing = indexing
        self.time_filter = time_filter

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
            value_ = f"'{values[i]}'" if type(values[i]) == str else values[i]
            # Replace \n with two spaces
            prop = f"{keys[i]}: " + str(value_).replace("\n", "  ") + ","
            props_str += prop + " "
        return "{" + props_str[:-2] + "}"  # Delete the comma and space at the end with [:-2]

    def node_code(self):
        """
        Denotes a node, to be used in defining relationships etc.
        """
        return f"({self.types_code()} {self.props_code()})"

    def merge_node_code(self):
        """
        We use MERGE instead of CREATE, so that a duplicate node
        should not be created in case the node exists.
        """
        return "MERGE " + self.node_code()


class Subreddit(Node):
    # https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html
    main_type = "Subreddit"
    available_types = ["Over18"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all"):
        super(Subreddit, self).__init__(api, name, limit, indexing, time_filter)
        self.resp = self.api.subreddit(self.name)

    @property
    def data(self):
        return {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "name": self.resp.display_name,
            "over18": self.resp.over18,
            "desc": self.resp.description,
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

    def __init__(self, api, name, limit, indexing="hot", time_filter="all"):
        super(Submission, self).__init__(api, name, limit, indexing, time_filter)
        self.resp = self.api.submission(self.name)

    @property
    def data(self):
        return {
            "id": self.resp.id,
            "created_utc": self.resp.created_utc,
            "title": self.resp.title,
            "text": self.resp.selftext,
            "archived": self.resp.archived,
            "stickied": self.resp.stickied,
            "locked": self.resp.locked,
            "over18": self.resp.over_18,
            "upvotes": self.resp.score,
            "upvote_ratio": self.resp.upvote_ratio,
            "edited": self.resp.edited
        }

    @property
    def author(self):
        username = self.resp.author.name
        return Redditor(self.api, username, limit=None)

    def comments(self):
        return self.resp.comments

    def __str__(self):
        return f"Submission(id={self.name})"


class Redditor(Node):
    # https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html
    main_type = "Redditor"
    available_types = ["Employee", "Mod", "Gold"]

    def __init__(self, api, name, limit, indexing="hot", time_filter="all"):
        super(Redditor, self).__init__(api, name, limit, indexing, time_filter)
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
        Return the submissions as a list of data_models.Submission objects

        Assuming that the user would look for every comments in submissions if they're
        searching submissions of a redditor, limit is set to None.
        (if not, they can fiddle with this at the Submission level)
        """
        subs = self.data["submissions"][self.indexing]
        ids = [sub.id for sub in subs]
        return [Submission(self.api, id_, limit=None) for id_ in ids]

    def comments(self):
        # Return a list of Comment objects instead of list
        # list is a band-aid solution
        return list(self.data["comments"][self.indexing])

    def __str__(self):
        return f"Redditor({self.name})"


class Relationship(ABC):
    """
    Abstract class to implement common properties of relationships
    and methods for Cypher code generation

    Relationships are always directional in Neo4j
    and our implementation will always be like
        (left_node)-[:RELATIONSHIP_TYPE]->(right_node)
    """
    def __init__(self, api: praw.Reddit, left_node: Node, right_node: Node):
        self.api = api
        self.left_node = left_node
        self.right_node = right_node


class Under(Relationship):
    rel_type = "UNDER"

    def __init__(self, api, submission, subreddit):
        super(Under, self).__init__(api, submission, subreddit)


class Moderates(Relationship):
    rel_type = "MODERATES"

    def __init__(self, api, redditor, subreddit):
        super(Moderates, self).__init__(api, redditor, subreddit)


class Authored(Relationship):
    rel_type = "AUTHORED"

    def __init__(self, api, redditor, submission):
        super(Authored, self).__init__(api, redditor, submission)


class Commented(Relationship):
    rel_type = "COMMENTED"

    def __init__(self, api, redditor, submission):
        super(Commented, self).__init__(api, redditor, submission)


class Replied(Relationship):
    rel_type = "REPLIED"

    def __init__(self, api, redditor_from, redditor_to):
        super(Replied, self).__init__(api, redditor_from, redditor_to)
