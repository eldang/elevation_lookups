# contributor guidelines

This needs to be fleshed out!

For now:

* run everything through `python3 -m flake8 *.py --ignore=E303,W504` before making a PR.
* Use mypy to check typing consistency.  It is AOK to tell it to ignore missing type hints from PEP imports, but all code in this project must have full type hints.
* Use a [virtual environment](https://docs.python.org/3/library/venv.html) to make sure that all Python dependencies are in [requirements.txt](requirements.txt) and all non-Python dependencies are described in [the readme](README.md).




## Roughly sketched out design

Data format: simple text files in which each row is one polyline, starting and ending at intersection middles.  Each row consists of a series of x,y coordinates separated by spaces; each coordinate is roughly a metre away from the previous.

Script: runs as a batch, processing the input file and producing a text file as output, with rows that correspond to the rows of the input file.  Each row simply reports four numbers: start elevation, end elevation, total climb, total descent.

Algorithm:
1. Parse input file, exiting with an error if there are any parse failures.  While parsing it, count lines and points, and compute a bounding box.
2. Use the bounding box to determine which data source to use, sticking to one consistent data source for one input file.  Use preferred local sources if available, falling back to a worldwide source (SRTM?) if not.
3. Store local copies of data sources, and track when they were saved.  TBD: do we want to just download the required bbox, that + some padding, or the whole data source?
4. Loop over the lines, computing the elevations and deltas as we go
5. Extra credit: where multiple data sources are available, is it useful to have the API check more than one and warn about discrepancies?

Program / data structure:

* main.py: main control loop
* files.py: defines objects for file operations:
	* input_file(): reads input files, reports stats back about them, and allows iteration through them
	* output_file(): opens output files and writes to them
* data.py: manages data sources and lookups
