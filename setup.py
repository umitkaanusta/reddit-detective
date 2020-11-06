from distutils.core import setup

from reddit_detective import VERSION

setup(
    name='reddit-detective',
    packages=['reddit_detective', 'reddit_detective.analytics'],
    version=VERSION,
    license='MIT',
    description='Play detective on Reddit',
    author='Ümit Kaan Usta',
    author_email='u.kaanusta@gmail.com',
    url='https://github.com/umitkaanusta/reddit-detective',
    download_url=f'https://github.com/umitkaanusta/reddit-detective/archive/v{VERSION}.tar.gz',
    keywords=["reddit", "data", "analysis", "analytics", "social",
              "network", "graph", "neo4j", "media", "news", "politics",
              "campaign", "information", "troll", "comment", "influencer",
              "idea", "spread", "campaign", "elections"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Sociology',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
