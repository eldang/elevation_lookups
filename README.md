# elevation

Some quick notes on the way to a scope of work to address https://github.com/a-b-street/abstreet/issues/82

## Data sources

1. SRTM as global baseline, overridden by preferred datasets where locally available
2. Seattle countours from https://data-seattlecitygis.opendata.arcgis.com/datasets/contour-lines-1993 - the notes warn against downloading it but it's actually only 189MB zipped / 304MB unzipped.  Looking closely at some areas I know well, the accuracy and detail both seem very good.
3. Possibility of using data that Access Maps has surveyed, but so far I think the contours will serve our needs better.
4. WA LIDAR https://lidarportal.dnr.wa.gov/#47.62076:-122.30622:18 - impressive detail, probably less convenient than using the contours where they exist.

## What data do we need exactly?

Thoughts so far:

1. Definitely elevation at the middle of each intersection, so we can calculate grades between them.
2. Probably also total climb for each line segment between two intersections, so that non-monotonic climbs aren't missed.
3. [setting this aside for now] Possibly also steepest segment characterisation, for unevenly steep blocks.

I'm also doing some research on what existing bike routefinding packages use.

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
* data.py: manages data sources

## Dependencies

This utility is being developed and tested in Python 3.9.2 on a Mac, and should in theory work with older versions of Python 3.  In addition to the Python modules listed in [requirements.txt](requirements.txt) it requires the following installed on the environment it will be run in:

* [GDAL](https://www.gdal.org/), tested with version 3.2.1, should in theory work with any version >= 3.0.4.
* [GEOS](https://trac.osgeo.org/geos), tested with version 3.9.1, should in theory work with any version >= 3.3.9.
* [PROJ](https://proj.org/), tested with version 7.2.1, should in theory work with any version >= 7.2.0.

These dependencies should be installed before the Python modules, so that they can be built to use what's present.  In addition, I recommend installing the Python modules with:

`pip3 install -r requirements.txt --no-binary pygeos --no-binary shapely`

to make sure that they are built with the exact versions of the above dependencies that are present in the environment.  This will make spatial lookup performance significantly faster.
