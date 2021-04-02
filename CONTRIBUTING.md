# Contributor guidelines

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](README.md#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thank you for your interest in contributing to this project!  There are many ways to help out, not all of which require coding skills.

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all interactions with this project.

## Ways to contribute

* File [bug reports](#Filing-bug-reports) and [feature requests](#feature-requests)
* Add to the [documentation](#Documentation)
* Translate the [documentation](#Documentation)
* Find local data sources
* Review issues & pull requests
* Fix existing issues
* Add features / code improvements

## Filing bug reports

If you use this tool and anything behaves unexpectedly, please let us know!  We ❤️ bug reports and they are intentionally first in the list of ways to contribute.  The project has a template set up for bug reports to help you include relevant information.  It is not necessary to fill out everything in that template, but the more you include the easier it will be for others to reproduce the bug and start fixing it.

Please note that errors in data sources are out of scope for this project.  If you are confident that you have found a data source error, please report it to the maintainer of that data source.  If you're not sure, then please do file a bug here, but please specify that you think the problem might be with the data so we can start by looking into that possibility.

## Feature requests

Feature requests are always welcome.  You don't need to know how to implement them, though if you do have ideas please include them.  Depending on relevance, complexity and contributors' availability we may not always be able to act on them quickly, but we will always acknowledge them and give you an expectation.  Responses may include "this is a good idea but it's going to be a while before I have time" or "this is out of scope, I suggest you fork the project to do it".

## Documentation

Clear, thorough [documentation](README.md) is essential for a tool to be useful.  Adding explanation, examples, or even just additional dependency versions that you've tested this project with are all much appreciated.

### Translations

Because this is a command line tool, translating the documentation is much higher priority than translating what little UI there is.  Translation of [the README](README.md) into any language will be very welcome.

## Adding data sources

For most of the world, this tool uses data from the Shuttle Radar Topography Mission.  It's pretty incredible that this resource exists, but it has some significant [resolution limitations](README.md#data-source-options).  Better local data sources are available for many areas.  If you find a better source


This needs to be fleshed out!

For now:

* run everything through `python3 -m flake8 *.py --ignore=E303,W504` before making a PR.
* Use mypy to check typing consistency.  It is AOK to tell it to ignore missing type hints from PEP imports, but all code in this project must have full type hints.
* Use a [virtual environment](https://docs.python.org/3/library/venv.html) to make sure that all Python dependencies are in [requirements.txt](requirements.txt) and all non-Python dependencies are described in [the readme](README.md).
* Also test the Docker build, if you weren't developing in that in the first place.




