from neo4j import BoltDriver


def get_redditors(driver: BoltDriver) -> list:
    s = driver.session()
    users = list(s.run("""
MATCH(r:Redditor) WITH r RETURN r.username
"""))
    return [user[0] for user in users]
