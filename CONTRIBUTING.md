# Contributing
This file contains
- resources for possible contributors
- how reddit-detective is managed (versioning etc.)
- issue and PR guidelines


## Resources for contributors
reddit-detective stands on the shoulders of two giants: PRAW and Neo4j.

PRAW (Python Reddit API Wrapper) is used to fetch data from Reddit. Neo4j is 
used to convert the outputs to a social network graph.

**PRAW documentation:** [PRAW Docs](https://praw.readthedocs.io/en/latest/)

**Learning to use Neo4j:** [Neo4j Online Training](https://neo4j.com/graphacademy/online-training/) 

**Introductory Social Network Analysis knowledge (optional):**
[E-Book: Social Network Analysis for Startups](https://www.oreilly.com/library/view/social-network-analysis/9781449311377/)


## Versioning
Starting from v0.1.1, reddit-detective uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Reporting a bug
Do **before** creating an issue for a bug:
1. **Use the GitHub issue search** — check if the issue has already been reported.
2. **Check if the issue has been fixed** — try to reproduce it using the latest 
master or development branch in the repository.

An example issue:
> Short and descriptive title
>
> A summary of the issue and the environment in which it occurs. If
> suitable, include the steps required to reproduce the bug.
>
> 1. This is the first step
> 2. This is the second step
> 3. Further steps, etc.
>
> Any other information you want to share that is relevant to the issue being
> reported. This might include the lines of code that you have identified as
> causing the bug, and potential solutions (and your opinions on their
> merits).


## Requesting a Feature
We welcome feature requests!

The procedure is similar to reporting a bug: Just create an issue
with an **enhancement** label.

To increase the chance of your feature request being approved:
- Learn about the scope and aims of reddit-detective
    - Don't hesitate to contact developers for more information!
- Make a strong case backed with solid arguments
- Provide as much as detail and context as possible


## Pull requests
Good pull requests - patches, improvements, new features - are a fantastic help. 
They should remain focused in scope and avoid containing unrelated commits.

Clueless about how to make a PR? [Read GitHub's tutorial](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)

To increase the chance of your PR being approved:
- Learn about the scope and aims of reddit-detective
    - Don't hesitate to contact developers for more information!
- Adhere to coding conventions of the project and PEP-8 style guide
- Make sure you add tests

**IMPORTANT**: By submitting a PR, you agree to allow the project owner to license your work under 
the same license as that used by the project.
