# Network
reddit-detective creates a social network graph by using Nodes and Degrees.
However, creating nodes and connecting them is not enough for our case.

We have to:

- Define constraints for the health of our database
- Solve the Karma Problem
- Provide an intuitive way of creating a social network graph

The RedditNetwork class solves these problems.

## What are constraints?
For our case, we define constraints **to ensure that each node is unique.**
Neo4j gives an error in case a query violates a constraint.

Since every node has a unique ID in Reddit API, we assert that the node's ID is unique.

By doing so, we avoid scenerios where two nodes of the same thing is created as a result of any unknown bug.

## What is the Karma Problem?
Let's assume that you get the subreddits they belong for 2 comments

*Terminology: **stuff like karma** includes
comment_karma, link_karma, score, upvote_ratio and subscribers*

If those 2 comments belong to the same subreddit, the code will be like the following:
```
MERGE (:Subreddit ...)
MERGE (:Subreddit ...)
```
If we include **stuff like karma** in properties at creation time,
then constraint UniqueSubreddit will fail.

**Why?**

Because Reddit does not give the exact number when it comes to
karmas/upvotes/subscribers for security purposes. This leads to having different karma numbers
in 2 MERGE statements for the same Subreddit, thus violating a constraint.

**What is our solution?**

- Do not include stuff like karma in properties at creation time
- After creation, get each node/rel's stuff like karma and add to their props
- **What if the user adds more stuff to their database?**
    - Delete each node/rel's stuff like karma
    - Then get each node/rel's stuff like karma and add to their props
- **What if the user does not want to deal with stuff like karma?**
    - Make it optional

## Code Samples
```python
from reddit_detective import RedditNetwork
from reddit_detective.data_models import Subreddit, Redditor
from reddit_detective.relationships import Comments, Submissions

# Constructing a social network
net = RedditNetwork(
        driver=driver,
        components=[
            Comments(Redditor(api, "BloodMooseSquirrel", limit=5)),
            Submissions(Subreddit(api, "learnpython", limit=5, indexing="new"))
        ]
    )

# Adding constraints
# Optional but highly recommended, doing once is enough
net.create_constraints()

# Running the code
net.run_cypher_code() # Call net.cypher_code() if you just want to get the code as a string

net.add_karma(api) # Shows karma as a property of nodes, optional
```

### How to dynamically add stuff to the database?
```python
# Assuming the imports are complete

net = RedditNetwork(
        driver=driver,
        components=[
            Comments(Redditor(api, "BloodMooseSquirrel", limit=5)),
            Submissions(Subreddit(api, "learnpython", limit=5, indexing="new"))
        ]
    )
# Assuming constraints are created, net.run_cypher_code() is executed
# and net.add_karma(api) is executed

# One way - without creating another network:
net.components.append(Comments(Redditor(api, "SomeGuy", limit=5)))
net.run_cypher_code()
net.add_karma(api)

# Another way:
net2 = RedditNetwork(
        driver=driver,
        components=[
            CommentsReplies(Redditor(api, "SomePerson123", limit=5)),
            Comments(Subreddit(api, "SomeSubreddit", limit=5, indexing="new"))
        ]
    )
# No need to create constraints again if constraints are created once for the database
net2.run_cypher_code()
net2.add_karma(api)
```

