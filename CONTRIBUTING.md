# Contributor guidelines

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](README.md#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thank you for your interest in contributing to this project!  There are many ways to help out, not all of which require coding skills.

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all interactions with this project.

## Ways to contribute

* File [bug reports](#Filing-bug-reports) and feature requests
* Add to the documentation
* Translate the documentation
* Find local data sources
* Review pull requests
* Fix existing issues
* Add features / code improvements

## Filing bug reports

If you use this tool and anything behaves unexpectedly, please let us know!  We ❤️ bug reports and they are intentionally first in the list of ways to contribute.


This needs to be fleshed out!

For now:

* run everything through `python3 -m flake8 *.py --ignore=E303,W504` before making a PR.
* Use mypy to check typing consistency.  It is AOK to tell it to ignore missing type hints from PEP imports, but all code in this project must have full type hints.
* Use a [virtual environment](https://docs.python.org/3/library/venv.html) to make sure that all Python dependencies are in [requirements.txt](requirements.txt) and all non-Python dependencies are described in [the readme](README.md).
* Also test the Docker build, if you weren't developing in that in the first place.




