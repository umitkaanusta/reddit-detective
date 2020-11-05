from neo4j import BoltDriver
from collections import OrderedDict


def get_redditors(driver: BoltDriver) -> list:
    s = driver.session()
    users = list(s.run("""
MATCH (r:Redditor) WITH r RETURN r.username
"""))
    return [user[0] for user in users]


def get_user_comments_times(driver: BoltDriver, username):
    s = driver.session()
    comments = list(s.run("""
MATCH (:Redditor {username: "%s"})-[:AUTHORED]-(c:Comment)-[:UNDER]-(s:Submission)
WITH c, s
RETURN c.id AS id, (c.created_utc - s.created_utc) / 1000 AS seconds_past
""" % username))
    comments = dict(comments)
    return list(comments.keys()), list(comments.values())


def get_submission_comments_times(driver: BoltDriver, submission_id):
    s = driver.session()
    comments = list(s.run("""
MATCH (s:Submission {id: "%s"})-[:UNDER]-(c:Comment)
WITH c, s
RETURN c.id AS id, (c.created_utc - s.created_utc) / 1000 AS seconds_past
""" % submission_id))
    comments = dict(comments)
    return list(comments.keys()), list(comments.values())


def get_subreddit_comments_times(driver: BoltDriver, subreddit_name):
    s = driver.session()
    comments = list(s.run("""
MATCH (:Subreddit {name: "%s"})-[:UNDER]-(s:Submission)-[:UNDER]-(c:Comment)
WITH c, s
RETURN c.id AS id, (c.created_utc - s.created_utc) / 1000 AS seconds_past
""" % subreddit_name))
    comments = dict(comments)
    return list(comments.keys()), list(comments.values())
