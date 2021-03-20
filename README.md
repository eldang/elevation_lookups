# elevation

Takes an input file of paths described as series of points, outputs a file of data about the elevation changes along those paths.

This is intended as a way of addressing https://github.com/a-b-street/abstreet/issues/82 but may be more broadly useful.

## Installation / requirements

This utility is being developed and tested in Python 3.9.2 on a Mac, and should in theory work with older versions of Python 3.  Before installing the modules listed in [requirements.txt](requirements.txt), make sure the following are present in the environment in which it will run:

* [GDAL](https://www.gdal.org/), tested with version 3.2.1, should in theory work with any version >= 3.0.4.
* [GEOS](https://trac.osgeo.org/geos), tested with version 3.9.1, should in theory work with any version >= 3.3.9.
* [PROJ](https://proj.org/), tested with version 7.2.1, should in theory work with any version >= 7.2.0.

Then install the Python modules with:

`pip3 install -r requirements.txt --no-binary pygeos --no-binary shapely`

to make sure that they are built with the exact versions of the above dependencies that are present in the environment.  This makes spatial lookups significantly faster.

### Docker

If you're having trouble getting dependencies installed, you can try Docker. Build the image locally by doing `docker build -t elevation_lookup .`. You can then use it by binding directories on your filesystem to the Docker container. Assuming you've created a file called `input/my_query`:

```
docker run \
  --mount type=bind,source=`pwd`/input,target=/elevation/input,readonly \
  --mount type=bind,source=`pwd`/data,target=/elevation/data \
  --mount type=bind,source=`pwd`/output,target=/elevation/output \
  -t elevation_lookups python3 main.py my_query
```

The output should appear in your local `output` directory.

## Basic usage

1. Put an input file in `input/`, and make sure `output/` and `data/` folders exist
2. `python3 main.py inputfilename`

## Data source options

By default, this project will use SRTM data to look up elevations.  This dataset has the advantage of global availability and ease of use, but it is limited by a 30m pixel size and 1m vertical resolution.  It is also possible to configure locally preferred data sources.  See [#adding-or-editing-data-sources](below) for details on how to add sources.  These are the available types and examples that are preconfigured in this project:

### Contour lines

Data files may be in any of the [https://gdal.org/drivers/vector/index.html](vector formats supported by GDAL), though note that for formats not marked as "Built-in by default" you may need to install additional prerequisites.  All common vector formats are supported by default.

The enclosed [datasources.json](datasources.json) sets up [https://data-seattlecitygis.opendata.arcgis.com/datasets/contour-lines-1993](Seattle's open 2ft contour dataset) as an example.

**Important note**: a point's elevation is taken only from the nearest contour to it, with no attempt to interpolate.  This works well for 2ft contours in a hilly area, but may become a significant source of error for flatter regions or more widely spaced contours.

### Raster elevation data

Data files may be in any of the [https://gdal.org/drivers/raster/index.html](raster formats supported by GDAL), though note that for formats not marked as "Built-in by default" you may need to install additional prerequisites.  All common raster formats are supported by default.

The enclosed [datasources.json](datasources.json) sets up "Delivery 1" from the Puget Sound LiDAR Consortium's [http://pugetsoundlidar.ess.washington.edu/lidardata/restricted/projects/2016king_county.html](2016 King County data) as an example.  It covers Seattle as well as some additional area S and E of Seattle.  Because it is defined after the Seattle 2ft contours, the contour dataset is used if it covers the required area, falling back to this LIDAR set for input files that are covered by it but not the contours.

## Input format

A text file in which each row is one path, and each row consists of tab-separated x,y coordinate pairs in order to describe a path, in unprojected decimal degrees.

## Output format

A text file in which each row corresponds to a row of the input, with order preserved, and consists of 4 tab-separated values that describe the elevation of the path in the input file, in metres rounded to the nearest mm:

`start_elevation	end_elevation	total_climb	total_descent`

Some things to note:

* Any non-zero `total_descent` is expressed as a positive value, i.e. a path that descends by 1 metre will have a value of 1
* `total_climb` and `total_descent` include intermediate ups and downs along the path, so it is not unusual for both to be non-zero, and in that case one of them will be larger than the difference between `start_elevation` and `end_elevation`
* (`start_elevation` - `end_elevation` + `total_climb` - `total_descent`) should always be within 1mm of 0.

## Adding or editing data sources

Data sources are defined in [datasources.json](datasources.json).  The order of entries in that file matters, because the first data source that covers all points in the input file will be used.  Each source is defined as an object in the JSON, with the following fields in any order (all fields are required, just set them to `null` when they don't apply):

* `name`: a name for human readability
* `url`: URL to download data from; if using a file that's already saved locally this field can be set to `null` or used to note the original source
* `filename`: a filename to save a local copy as, into the data/ directory
*	`crs`: the coordinate reference system of the original data file as a string in the format "EPSG:4326".  Any CRS that PROJ can handle works; files will be converted to EPSG:4326 on loading if they aren't already in that
* `bbox`: WSEN coordinates for the area covered by this file
* `download_method`: how to obtain the file.  Currently supported values:
	* `http`: download http resource
	* `ftp`: download ftp resource.  *NB: this is anonymous-only; authentication is not yet supported*
	* `local`: don't fetch the file, assume that it already exists at `filename`
* `lookup_method`: how to read elevations out from this file.  Currently supported values:
	* `contour_lines`: each point is tagged with the elevation of the nearest contour
	* `raster`: each point will get its elevation from the raster pixel it falls in
* `lookup_field`: for vector data, this is the name of the field that actually has elevations in it; for raster data this is the band number.  Note that raster bands are 1-indexed, so for a 1-band raster the correct value of this field is 1
* `units`: units of elevation; will be converted to metres if they aren't already
* `recheck_interval_days`: how often to check for updates to the original source file; set to `null` to never check

