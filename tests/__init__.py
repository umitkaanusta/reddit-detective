import json
import praw

from reddit_detective import VERSION

with open("test_credentials.json") as test_cred_file:
    test_cred = json.load(test_cred_file)

api_ = praw.Reddit(
    client_id=test_cred["client_id"],
    client_secret=test_cred["client_secret"],
    user_agent=f"reddit-detective/{VERSION}"
)
