============
Contributing
============

We accept patches through Github pull requests.

==========
Code Style
==========

Please run the following commands and ensure they continue to pass::

    pyre check
    flake8
    black .

Other than that, use the style of the code surrounding your change as a guide to code style.

=====
Tests
=====

Before making a pull request, please verify that the test suite passes.
The test suite can be run with ``python3 -m unittest discover test`` from the project root directory.
If your changes cause the tests to fail please update the tests and mention it in your pull request.

In addition, please update the documentation if it is relevant to your changes.

