# contributor guidelines

This needs to be fleshed out!

For now:

* run everything through `python3 -m flake8 *.py --ignore=E303,W504` before making a PR.
* Use mypy to check typing consistency.  It is AOK to tell it to ignore missing type hints from PEP imports, but all code in this project must have full type hints.
* Use a [virtual environment](https://docs.python.org/3/library/venv.html) to make sure that all Python dependencies are in [requirements.txt](requirements.txt) and all non-Python dependencies are described in [the readme](README.md).
