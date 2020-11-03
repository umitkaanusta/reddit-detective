from neo4j import BoltDriver

from reddit_detective.analytics.utils import get_redditors


def interaction_score(driver: BoltDriver, username):
    """
    For a user in the Graph, shows
        # comments received / # comments received + # comments made

    Best practice is to use it in networks with nodes with limit=None

    Inspired from "Analyzing behavioral trends in community driven
    discussion platforms like Reddit"
    DOI: 10.1109/ASONAM.2018.8508687

    Score close to 1: User is a "starter"
    Score close to 0: User is a "consumer"
    """
    s = driver.session()
    comments_received = list(s.run("""
MATCH (:Redditor {username: "%s"})-[:AUTHORED]-(:Submission)-[:UNDER]-(c:Comment)
WITH c
RETURN count(c)
""" % username))[0][0]  # Converted Result object to integer
    comments_made = list(s.run("""
MATCH (:Redditor {username: "%s"})-[:AUTHORED]-(c:Comment)
WITH c
RETURN count(c)
""" % username))[0][0]
    return comments_received / (comments_received + comments_made)


def interaction_score_normalized(driver: BoltDriver, username):
    users_score = interaction_score(driver, username)
    total_score = sum([interaction_score(driver, user) for user in get_redditors(driver)])
    return users_score / total_score
