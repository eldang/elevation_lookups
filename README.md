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

## Data sources

1. SRTM as global baseline, overridden by preferred datasets where locally available [TODO: not yet implemented]
2. Seattle countours from https://data-seattlecitygis.opendata.arcgis.com/datasets/contour-lines-1993
3. Adding other local data sources is straightforward if they are of an equivalent type to one already in use, and achievable if not.

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

Data sources are defined in [datasources.json](datasources.json).  The order of entries in that file matters, because the utility will use the first data source that covers all points in the input file.  Each source is defined as an object in the JSON, as in this example (note that JavaScript-style comments aren't allowed in an actual JSON file):

```javascript
{
	"name": "Seattle 2ft contours", // a name for human readability only
	"url": "https://opendata.arcgis.com/datasets/1545ab0b0fcc492886be92be25a9faa5_0.geojson",
	"filename": "seattle_contours.geojson", // a filename to save a local copy as, into the data/ directory
	"crs": "EPSG:4326", // the coordinate reference system of the original data file.  Any CRS that PROJ can handle works; files will be converted to EPSG:4326 on loading if they aren't already in that
	"bbox": [-122.4359526776817120,47.4448428851168060, -122.2173553791662357,47.7779711955390596], // WSEN coordinates for the area covered by this file
	"lookup_method": "contour_lines", // how to parse this file.  Has to have a pathway set up in data.py
	"lookup_field": "CL93_ELEV", // the name of the field that actually has elevations in it
	"units": "feet", // units of elevation; will be converted to metres if they aren't already
	"recheck_interval_days": 30 // how often to check for updates to the original source file
}
```

Currently, `contour_lines` is the only supported `lookup_method`.



