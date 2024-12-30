import os
from codecs import open
from typing import Any

from setuptools import find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "pyavrio", "_version.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open(os.path.join(here, "README.md"), "r", "utf-8") as f:
    readme = f.read()

kerberos_require = ["requests_kerberos"]
sqlalchemy_require = ["sqlalchemy >= 1.3"]
external_authentication_token_cache_require = ["keyring"]
all_require = kerberos_require + sqlalchemy_require

tests_require = all_require + [
    "httpretty < 1.1",
    "pytest",
    "pytest-runner",
    "pre-commit",
    "black",
    "isort",
]

setup(
    name=about["__title__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    version=about["__version__"],
    url=about["__url__"],
    packages=find_packages(include=["pyavrio", "pyavrio.*"]),
    package_data={"": ["LICENSE", "README.md"]},
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Database :: Front-Ends",
    ],
    python_requires=">=3.8",
    install_requires=[
        "backports.zoneinfo;python_version<'3.9'",
        "python-dateutil",
        "pytz",
        # requests CVE https://github.com/advisories/GHSA-j8r2-6x86-q33q
        "requests>=2.31.0",
        "tzlocal",
        "sqlalchemy >= 1.3",
        "sql_metadata==2.11.0"
    ],
    extras_require={
        "all": all_require,
        "kerberos": kerberos_require,
        "sqlalchemy": sqlalchemy_require,
        "tests": tests_require,
        "external-authentication-token-cache": external_authentication_token_cache_require,
    },
    entry_points={
        "sqlalchemy.dialects": [
            "pyavrio = pyavrio.sqlalchemy.dialect:TrinoDialect",
        ]
    },
)
