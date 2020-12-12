# Relationships
Relationships in reddit-detective are essential because of two reasons:

1. That's the way how we navigate in the social network graph

    - Example: Assume Jack loves Tina and Tina loves Harry. 
    We can show this as **Jack-[Loves]->Tina-[Loves]->Harry**
    (not the actual way of showing relationships in Cypher, treat this as some form of a pseudocode)
    - Now assume that we're going to look for the percentage of bi-directional "Loves" relationships.
    We'll do the counting by using "roads" created by nodes and relationships.
2. They are mediators just like Nodes (see Data Models for detailed explanation of a mediator)

## How do Relationships work?
Relationships of a Node are created according to the given Degree. (see Data Models to learn what a Degree is)

### Submissions Degree - how does it work?
Can be used by: Subreddit, Redditor

1. Get submissions for the given node from Reddit API
2. Get the author and subreddit for each submission
3. Generate Cypher code to Create nodes for all submissions, subreddits and authors
4. Generate Cypher code to Link Submissions to Subreddits (with **UNDER** relationship)
5. Generate Cypher code to Link Authors to Submissions (with **AUTHORED** relationship)

### Comments Degree - how does it work?
Can be used by: Subreddit, Submission, Redditor

0. All of the above (Submissions degree)
1. Get comments for each submission
2. Generate Cypher code to Create nodes for all comments
3. Generate Cypher code to link Comments to Submissions (with **UNDER** relationship)
4. Generate Cypher code to link Authors to Comments (with **AUTHORED** relationship)

### Replies Degree - how does it work?
Can be used by: Subreddit, Submission, Redditor

**Note that the Replies degree might have a higher time complexity when dealing with bigger data**

0. All of the above (Comments degree)
1. Get replies for each comment
2. Generate Cypher code to link Comments to replies (which are also Comments) (with **UNDER** relationship)

## Code Samples
```python
from reddit_detective.data_models import Redditor
from reddit_detective.relationships import Submissions, Comments, CommentsReplies

subs = Submissions(Redditor(api_, "Anub_Rekhan", limit=2))
subs.code()  # Returns the generated Cypher code 
```
**Q: How can I run this Cypher code and see the results in my Neo4j database?**

- You can only run Cypher codes through RedditNetwork objects,
see Network for detailed information

**Q: Why can't I run the Cypher code without a RedditNetwork object?**

- RedditNetwork objects are also a gate to solve the Karma Problem we've encountered.
What is that? - See Network for detailed information. 
