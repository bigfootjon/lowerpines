# pyre-ignore-all-errors
from distutils.core import setup

import setuptools  # type: ignore

import lowerpines

with open("README.rst", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="lowerpines",
    package_data={"lowerpines": ["py.typed"]},
    packages=setuptools.find_packages(exclude=["test", "test.*"]),
    version=lowerpines.VERSION,
    python_requires=">=3.6",
    description="Library wrapper for GroupMe API",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=["requests"],
    license="GNU Lesser General Public License v3 (LGPLv3)",
    author="Jonathan Janzen",
    author_email="jjjonjanzen@gmail.com",
    url="https://github.com/bigfootjon/lowerpines",
    download_url="https://github.com/bigfootjon/lowerpines/tarball/"
    + lowerpines.VERSION,
    keywords=["api", "GroupMe"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Typing :: Typed",
    ],
)
