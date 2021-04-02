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
* Find [local data sources](#Adding-data-sources)
* Review [issues](#reviewing-new-issues) & [pull requests](#reviewing-pull-requests)
* [Fix existing issues](#fixing-issues)
* [Add features / code improvements](#adding-features-or-improving-code)

## Filing bug reports

If you use this tool and anything behaves unexpectedly, please let us know!  We ❤️ bug reports and they are intentionally first in the list of ways to contribute.  The project has a template set up for bug reports to help you include relevant information.  It is not necessary to fill out everything in that template, but the more you include the easier it will be for others to reproduce the bug and start fixing it.

Please note that errors in data sources are out of scope for this project.  If you are confident that you have found a data source error, please report it to the maintainer of that data source.  If you're not sure, then please do file a bug here, but please specify that you think the problem might be with the data so we can start by looking into that possibility.

## Feature requests

Feature requests are always welcome.  You don't need to know how to implement them, though if you do have ideas please include them.  Depending on relevance, complexity and contributors' availability we may not always be able to act on them quickly, but we will always acknowledge them and give you an expectation.  Responses may include "this is a good idea but it's going to be a while before I have time" or "this is out of scope, I suggest you fork the project to do it".

## Documentation

Clear, thorough [documentation](README.md) is essential for a tool to be useful.  Adding explanation, examples, or even just additional dependency versions that you've tested this project with are all much appreciated.

### Translations

Because this is a command line tool, translating the documentation is a much higher priority than translating what little UI there is.  Translation of [the README](README.md) into any language will be very welcome.

## Adding data sources

For most of the world, this tool uses data from the Shuttle Radar Topography Mission.  It's pretty incredible that this resource exists, but it has some significant [resolution limitations](README.md#data-source-options).  Better local data sources are available for many areas.  If you find a better source for an area you know well enough to evaluate results, please make a pull request adding it to [datasources.json](datasources.json).  If you don't know how to do that, then please submit a [feature request](#feature-requests) giving as much detail as possible about the source, so someone else can add it.

## Reviewing others' contributions

Please take note of the [Code of Conduct](CODE_OF_CONDUCT.md) and generally be kind with reviews.  This is an opportunity to really set the tone for a project, use it well.

### Reviewing new issues

It's always helpful to look at recently filed issues, and check for the following:

* Does the issue include all required information, or do we need to ask the poster for any clarifications?
* If it's a bug, can you reproduce it?  If you learn anything from reproducing it, leave a comment.
* If it could be a data source bug, can you identify whether it is that or a bug in this project?
* Is it worth adding any tags?
* Do you have ideas about how to fix it?  Even if you don't have time to implement them, commenting with the suggestion is helpful.

### Reviewing pull requests

Every pull request needs at least one code review before it can be merged.  The maintainer[s] will always try to do these quickly, but if you see a PR that hasn't been reviewed yet you can help.  Please check the following:

* Can you run it?
* If there's new code, is it clearly written and/or commented?
* Does it meet the [coding standards](#coding-standards)?

## Fixing issues

Feel free to attempt a fix for any issue that hasn't already been assigned to a person.  Please assign yourself or comment on the issue so that others can know it's already being worked on, and follow the [coding standards](#coding-standards).

Issues that most need help are tagged `help wanted`, and issues that are likely to be relatively self-contained ways to get started are tagged `good first issue`.

## Adding features or improving code

If you want to add or fix anything that doesn't already have an open issue for it, please first search closed issues in case it's already been discussed.  If it hasn't, then we recommend first filing an issue and asking for feedback.  In an effort to keep this tool focussed, there are many good ideas for which we would suggest forking the project, and it can save a lot of time and effort to get that feedback up front.

That said, there are many ways this code base could be improved, and attempts are welcome.  Please follow these coding standards:

### Coding standards

This project uses Python 3 with classes and [type hints](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html).  Please use these tools before making a pull request, to ensure code quality and consistency:

* Run everything through `python3 -m flake8 *.py --ignore=E303,W504` and either implement its suggestions or explicitly comment exceptions.
* Use `mypy main.py` to check typing consistency and fix any issues it raises.  It is AOK to tell it to ignore missing type hints from PEP imports, but all code in this project must have full type hints.
* Use a [virtual environment](https://docs.python.org/3/library/venv.html) to make sure that all Python dependencies are in [requirements.txt](requirements.txt) and all non-Python dependencies are described in [the readme](README.md).
* Also test the Docker build, if you weren't developing in that in the first place.
* If you are adding any dependencies, please note that in the pull request and explain what they are for.
* If you are adding or changing any functionality, please update [the readme](README.md) to reflect your changes.

