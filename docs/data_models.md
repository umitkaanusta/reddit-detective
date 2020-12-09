# Data Models
reddit-detective defines classes to denote a "Node" in the Reddit Network.

By using "Node"s as mediators, we ease the process of converting 
Reddit data to Cypher (Neo4j's query language) code.


# Nodes
Nodes are designed to do three things:
1. Get data from Reddit API and store it (Extract)
2. Adjust the data to be compatible with Neo4j (Transform)
3. Generate Cypher code from adjusted data (Load-ish)

In other words, Nodes are our little ETL helpers, helping simplify a relatively complex process.

## Degrees
A **degree** is a string showing the furthermost you can go when looking at connections of a node.

Node types Subreddit, Submission, Redditor have attributes showing their available degrees.

For instance, a Subreddit node has `[submissions, comments, replies]` as available degrees.
- Submissions: Get the subreddit node, connect it with submissions under it
- Comments: Do what the previous degree does + connect submissions to comments under them
    - This gets all the comments, not just the top comments in comment trees.
- Replies: Do what the previous degree does + connect comments to each other by finding
which one is a reply to the other

To see how degrees are implemented, see Relationships

## Node Types
Major types (Subreddit, Submission, Comment, Redditor) are denoted with a **class**

Minor types (e.g Redditor has Employee, Suspended) are shown as a
list of strings in available_types attribute of each major type.

- **Redditor** (Inherits from Node)
    - Available types: Employee, Suspended
    - Available degrees: Submissions, Comments, Replies
    - Properties: `"id", "username", "created_utc", "has_verified_email", "employee", "suspended"`
        - If suspended: `"id", "username", "employee", "suspended"`
    
- **Submission** (Inherits from a helper class SubOrComment which inherits from Node)
    - Available types: Archived, Stickied, Locked, Over18
    - Available degrees: Comments, Replies
    - Properties: `"id", "created_utc", "title", "text", "archived", "stickied", "locked", "over18"`
    
- **Subreddit** (Inherits from Node)
    - Available types: Over18
    - Available degrees: Submissions, Comments, Replies
    - Properties: `"id", "created_utc", "name", "over18", "desc"`

- **Comment** (Inherits from a helper class SubOrComment which inherits from Node)
    - Comments do not have minor types
    - Comments do not have degrees, since there isn't a component smaller than a Comment.
        - Replies to comments are Comment objects too
    - Properties: `"id", "created_utc", "text", "is_submitter", "stickied"`
    
## Sample Code
```python
from reddit_detective.data_models import Subreddit

sub = Subreddit(api_, "learnpython", limit=100)
print(red.merge_code())

# Output
# MERGE (:Subreddit {id: "2r8ot", created_utc: 1254499181.0, name: "learnpython", desc: "..."})
# desc is truncated since the actual desc is too long 
```

      
# Relationship types
In Neo4j, two nodes can have directed relationships connecting one to the other, allowing us to create a network.

Relationships can also have properties, e.g relationship `LIKES` might have a boolean property `is_crush`

Below there are three types of relationships with the types of nodes they connect shown in this format:
(Node1 -> Node2)

- **MODERATES**
    - (Redditor -> Subreddit)
    - No properties
    
- **UNDER**
    - (Submission -> Subreddit)
    - (Comment -> Submission)
    - (Comment -> Comment)
    - No properties
    
- **AUTHORED**
    - (Redditor -> Submission) 
    - (Redditor -> Comment)
    - No properties

For detailed information about relationship types, see Relationships
