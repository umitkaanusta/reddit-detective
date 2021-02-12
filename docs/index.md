# reddit-detective: Play detective on Reddit
![Python version](https://img.shields.io/badge/python-v3.7-blue)
![Neo4j version](https://badgen.net/badge/neo4j/v4.1.0/cyan)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)
[![Documentation Status](https://readthedocs.org/projects/reddit-detective/badge/?version=latest)](https://reddit-detective.readthedocs.io/en/latest/?badge=latest)

```
pip install reddit_detective
```

**reddit-detective** represents reddit in a graph structure using Neo4j. 

Created to help researchers, developers and people who are curious about
how Redditors behave.


## Helping you to:
- Detect political disinformation campaigns
- Find trolls manipulating the discussion
- Find secret influencers and idea spreaders (it might be you!)
- Detect "cyborg-like" activities
    - "What's that?" Check `reddit_detective/analytics/metrics.py` for detailed information


## Installation and Usage
- Install Neo4j 4.1.0 [here](https://neo4j.com/docs/operations-manual/current/installation/)
- Neo4j uses Cypher language as its query language. 
Knowing Cypher dramatically increases what you can do with reddit-detective 
[Click here to learn Cypher](https://neo4j.com/graphacademy/online-training/introduction-to-neo4j-40/)
- Install reddit-detective with `pip install reddit_detective`
    - **Note:** Version 0.1.2 is broken, any other version is fine


## Code Samples

### Creating a Reddit network graph
```python
import praw
from neo4j import GraphDatabase

from reddit_detective import RedditNetwork, Comments
from reddit_detective.data_models import Redditor

# Create PRAW client instance
api = praw.Reddit(
    client_id="yourclientid",
    client_secret="yourclientsecret",
    user_agent="reddit-detective"
)

# Create driver instance
driver = GraphDatabase.driver(
    "url_of_database",
    auth=("your_username", "your_password")
)

# Create network graph
net = RedditNetwork(
        driver=driver,
        components=[
            # Other relationship types are Submissions and CommentsReplies
            # Other data models available as components are Subreddit and Submission
            Comments(Redditor(api, "BloodMooseSquirrel", limit=5)),
            Comments(Redditor(api, "Anub_Rekhan", limit=5))
        ]
    )
net.create_constraints() # Optional, doing once is enough
net.run_cypher_code()
net.add_karma(api)  # Shows karma as a property of nodes, optional
```
**Output (in Neo4j):**
![Result](docs/images/network_img.PNG)


### Finding interaction score
```python
# Assuming a network graph is created and database is started

# Interaction score = A / (A + B)
# Where A is the number of comments received in user's submissions
# And B is the number of comments made by the user
from reddit_detective.analytics import metrics

score = metrics.interaction_score(driver, "Anub_Rekhan")
score_norm = metrics.interaction_score_normalized(driver, "Anub_Rekhan")
print("Interaction score for Anub_Rekhan:", score)
print("Normalized interaction score for Anub_Rekhan:", score_norm)
```
**Output:**
```
Interaction score for Anub_Rekhan: 0.375
Normalized interaction score for Anub_Rekhan: 0.057324840764331204
```


### Finding cyborg score
```python
# Assuming a network graph is created and database is started

# For a user, submission or subreddit, return the ratio of cyborg-like comments to all comments
# A cyborg-like comment is basically a comment posted within 6 seconds of the submission's creation
# Why 6? Can't the user be a fast typer? 
#   See reddit_detective/analytics/metrics.py for detailed information

from reddit_detective.analytics import metrics

score, comms = metrics.cyborg_score_user(driver, "Anub_Rekhan")
print("Cyborg score for Anub_Rekhan:", score)
print("List of Cyborg-like comments of Anub_Rekhan:", comms)
```
**Output:**
```
Cyborg score for Anub_Rekhan: 0.2
List of Cyborg-like comments of Anub_Rekhan: ['q3qm5mo']
```


### Running a Cypher statement
```python
# Assuming a network graph is created and database is started

session = driver.session()
result = session.run("Some cypher code")
session.close()
```


## Upcoming features
- [ ] UserToUser relationships
    - A relationship to link users with its only property being the amount of **encounters**
    - Having ties with the same submission is defined as an **encounter**
- [ ] Create a wrapper for centrality metrics of Neo4j GDSC (Graph data science library)


## Inspirations
List of works/papers that inspired reddit-detective:
```
authors: [Sachin Thukral (TCS Research), Hardik Meisheri (TCS Research),
Arnab Chatterjee (TCS Research), Tushar Kataria (TCS Research),
Aman Agarwal (TCS Research), Lipika Dey (TCS Research),
Ishan Verma (TCS Research)]

title: Analyzing behavioral trends in community driven
discussion platforms like Reddit

published_in: 2018 IEEE/ACM International Conference on Advances in 
Social Networks Analysis and Mining (ASONAM)

DOI: 10.1109/ASONAM.2018.8508687
```
