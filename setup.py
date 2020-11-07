import setuptools

from reddit_detective import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reddit_detective",
    packages=["reddit_detective", "reddit_detective.analytics"],
    license="MIT",
    version=VERSION,
    author="Ümit Kaan Usta",
    author_email="u.kaanusta@gmail.com",
    url="https://github.com/umitkaanusta/reddit-detective",
    description="Play detective on Reddit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["reddit", "data", "analysis", "analytics", "social",
              "network", "graph", "neo4j", "media", "news", "politics",
              "campaign", "information", "troll", "comment", "influencer",
              "idea", "spread", "campaign", "elections"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Sociology",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=["praw", "neo4j"]
)
