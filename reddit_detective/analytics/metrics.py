from neo4j import BoltDriver

from reddit_detective.analytics.utils import (get_redditors, get_user_comments_times,
    get_submission_comments_times, get_subreddit_comments_times)


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


def _cyborg_score(driver: BoltDriver, name, util_func) -> tuple:
    """
    Calculates the ratio of cyborg-like comments to all comments of the user.

    Tuple's first element is the score, second element is a list of
    ids of the cyborg-like comments.

    Inspired from "Analyzing behavioral trends in community driven
    discussion platforms like Reddit"
    DOI: 10.1109/ASONAM.2018.8508687

    At a subreddit, 17%-20% of the people exhibit such cyborg-like behaviors.
    If a post's first comment is made within 6 seconds, the chances
    of it being cyborg-like is 79%-83.9% according to the paper.
    This information is extracted by looking at the character sizes of those
    comments.

    A Cyborg-like comment can also be an advertisement,
    AutoModerator post or a copy-paste.
    """
    cyborg_comms = []
    ids, times = util_func(driver, name)
    for i in range(len(ids)):
        if times[i] <= 6:
            cyborg_comms.append(ids[i])
    return len(cyborg_comms) / len(ids), cyborg_comms


def cyborg_score_user(driver: BoltDriver, username):
    return _cyborg_score(driver, username, util_func=get_user_comments_times)


def cyborg_score_submission(driver: BoltDriver, submission_id):
    return _cyborg_score(driver, submission_id, util_func=get_submission_comments_times)


def cyborg_score_subreddit(driver: BoltDriver, subreddit_name):
    return _cyborg_score(driver, subreddit_name, util_func=get_subreddit_comments_times)
