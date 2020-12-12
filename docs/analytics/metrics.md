# Metrics
Reddit-detective implements scientifically proven metrics for social networks, as a way of inspecting
the anatomy of the social network.

## Interaction score
For a Redditor in the graph,
- Interaction score = # Comments received / (# Comments received + # Comments made)
- Score close to 0: User is a **starter**
- Score close to 1: User is a **consumer**

Best practice is to use it in networks with nodes with limit=None

Inspired from: "Analyzing behavioral trends in community driven
discussion platforms like Reddit" (DOI: 10.1109/ASONAM.2018.8508687)
    
```python
from reddit_detective.analytics import metrics
# Assuming a network graph is created and database is started

score = metrics.interaction_score(driver, "Anub_Rekhan")
score_norm = metrics.interaction_score_normalized(driver, "Anub_Rekhan")
print(score)  # 0.375
print(score_norm) # 0.057324840764331204
```

## Cyborg score
For a Redditor, Submission or a Subreddit in the graph,
- Cyborg score = # Cyborg-like comments / # All comments 
- Cyborg-like comment: Comment posted under a submission within 6 seconds of its creation

At a subreddit, 17%-20% of the people exhibit such cyborg-like behaviors.
If a post's first comment is made within 6 seconds, the chances
of it being cyborg-like is 79%-83.9% according to the paper.
This information is extracted by looking at the character sizes of those
comments.

**Note that a Cyborg-like comment can also be an advertisement,
AutoModerator post or a copy-paste.**
    
Inspired from: "Analyzing behavioral trends in community driven
discussion platforms like Reddit" (DOI: 10.1109/ASONAM.2018.8508687)

```python
# Assuming a network graph is created and database is started

from reddit_detective.analytics import metrics

# Tuple's first element is the score, 
# second element is the list of IDs of the cyborg-like comments
score, comms = metrics.cyborg_score_user(driver, "Anub_Rekhan")
print(score)  # 0.2
print(comms)  # ['q3qm5mo']
```
