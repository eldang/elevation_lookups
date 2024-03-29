# elevation
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Takes an input file of paths described as series of points, outputs a file of data about the elevation changes along those paths.

This is intended as a way of addressing https://github.com/a-b-street/abstreet/issues/82 but may be more broadly useful.

## Installation / requirements

This utility is being developed and tested in Python 3.9.2 on a Mac & 3.8.5 on Linux, and should in theory work with older versions of Python 3.  Before installing the modules listed in [requirements.txt](requirements.txt), make sure the following are present in the environment in which it will run:

* [GDAL](https://www.gdal.org/), tested with versions 3.2.0 - 3.2.2, should in theory work with any version >= 3.0.4.
* [GEOS](https://trac.osgeo.org/geos), tested with versions 3.6.2 & 3.9.1, should in theory work with any version >= 3.3.9.
* [PROJ](https://proj.org/), tested with versions 7.2.1 & 8.0.0, should in theory work with any version >= 7.2.0.

Then install the Python modules with:

`pip3 install -r requirements.txt --no-binary pygeos --no-binary shapely`

to make sure that they are built with the exact versions of the above dependencies that are present in the environment.  This makes spatial lookups significantly faster.

### Docker

If you're having trouble getting dependencies installed, you can try Docker. Build the image locally by doing `docker build -t elevation_lookups .`. You can then use it by binding directories on your filesystem to the Docker container. Assuming you've created a file called `input/my_query`:

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

To specify how many parallel processes will be spawned to process the input, add the argument `--n_threads=X`.  If X == 1 then parallel processing will be sidestepped entirely; this can be useful for debugging.  If this argument is not set, then the script will default to using as many processes as CPUs are present.  **Note that parallel raster processing can have a heavy memory footprint**: specifically, each parallel process loads its own copy of the elevation data source, windowed to the bounding box of the input data.  So for a large area and a high resolution raster data source, memory may be a tighter practical constraint on parallel processing than CPU availability.

## Data source options

By default, this project will use SRTM data to look up elevations.  This dataset has the advantage of global availability and ease of use, but it is limited by a coarse pixel size and 1m vertical resolution.  The pixel size between 56S and 60N is 0.00027̅°, which equates to 30m E-W at the equator and 15m E-W at 60N, and 30m N-S at any latitude.  In theory, the pixels triple in size at latitudes outside the range (56S, 60N), though in testing we are still finding 0.00027̅° pixels for Anchorage, Alaska, USA (> 61N).

It is also possible to configure locally preferred data sources.  See [below](#adding-or-editing-data-sources) for details on how to do so.  These are the available types and examples that are preconfigured in this project:

### Contour lines

Data files may be in any of the [vector formats supported by GDAL](https://gdal.org/drivers/vector/index.html), though note that for formats not marked as "Built-in by default" you may need to install additional prerequisites.  All common vector formats are supported by default.

The enclosed [datasources.json](datasources.json) sets up [Seattle's open 2ft contour dataset](https://data-seattlecitygis.opendata.arcgis.com/datasets/contour-lines-1993) as an example.  Because it is defined after the LIDAR data, the LIDAR dataset is used if it covers the required area, falling back to this contour set for input files that are covered by it but not the LIDAR.  In practice this means it will very rarely be used; consider it more a demo than a practical feature.  In our testing we've found that the LIDAR data gets us very similar results in a fraction of the processing time.

**Important note**: a point's elevation is taken only from the nearest contour to it, with no attempt to interpolate.  This works well for 2ft contours in a hilly area, but may become a significant source of error for flatter regions or more widely spaced contours.

### Raster elevation data

Data files may be in any of the [raster formats supported by GDAL](https://gdal.org/drivers/raster/index.html), though note that for formats not marked as "Built-in by default" you may need to install additional prerequisites.  All common raster formats are supported by default.

The enclosed [datasources.json](datasources.json) sets up "Delivery 1" from the Puget Sound LiDAR Consortium's [2016 King County data](http://pugetsoundlidar.ess.washington.edu/lidardata/restricted/projects/2016king_county.html) as an example.  It covers Seattle as well as some additional area S and E of Seattle.

## Input format

A text file in which each row is one path, and each row consists of tab-separated x,y coordinate pairs in order to describe a path, in unprojected decimal degrees.  The file should contain no blank lines until the end, as input parsing will stop at the first blank line it encounters.

## Output format

A text file in which each row corresponds to a row of the input, with order preserved, and consists of 4 tab-separated values that describe the elevation of the path in the input file, in metres rounded to the nearest mm:

`start_elevation	end_elevation	total_climb	total_descent`

Some things to note:

* Any non-zero `total_descent` is expressed as a positive value, i.e. a path that descends by 1 metre will have a value of 1
* `total_climb` and `total_descent` include intermediate ups and downs along the path, so it is not unusual for both to be non-zero, and in that case one of them will be larger than the difference between `start_elevation` and `end_elevation`
* (`start_elevation` - `end_elevation` + `total_climb` - `total_descent`) should always be within 1mm of 0.
* If the utility is unable to find elevations for any of the points in a given input line, it will write a blank line to the output file.
* If the utility is able to find elevations for some but not all of the points in an input line, it will assume that the missing points have the same elevation as their neighbours.

## Adding or editing data sources

Data sources are defined in [datasources.json](datasources.json).  The order of entries in that file matters, because the first data source that covers all points in the input file will be used.  Each source is defined as an object in the JSON, with the following fields in any order (all fields are required, just set them to `null` when they don't apply):

* `name`: a name for human readability
* `url`: URL to download data from; if using a file that's already saved locally this field can be set to `null` or used to note the original source
* `filename`: a filename to save a local copy as, into the data/ directory, or at which to find a pre-saved local copy
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


## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://eldang.xyz/"><img src="https://avatars.githubusercontent.com/u/1379812?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Eldan Goldenberg</b></sub></a><br /><a href="https://github.com/eldang/elevation_lookups/issues?q=author%3Aeldang" title="Bug reports">🐛</a> <a href="https://github.com/eldang/elevation_lookups/commits?author=eldang" title="Code">💻</a> <a href="https://github.com/eldang/elevation_lookups/commits?author=eldang" title="Documentation">📖</a> <a href="#projectManagement-eldang" title="Project Management">📆</a> <a href="https://github.com/eldang/elevation_lookups/pulls?q=is%3Apr+reviewed-by%3Aeldang" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="http://abstreet.org"><img src="https://avatars.githubusercontent.com/u/1664407?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dustin Carlino</b></sub></a><br /><a href="https://github.com/eldang/elevation_lookups/issues?q=author%3Adabreegster" title="Bug reports">🐛</a> <a href="https://github.com/eldang/elevation_lookups/commits?author=dabreegster" title="Code">💻</a> <a href="#data-dabreegster" title="Data">🔣</a> <a href="#financial-dabreegster" title="Financial">💵</a> <a href="#ideas-dabreegster" title="Ideas, Planning, & Feedback">🤔</a> <a href="#platform-dabreegster" title="Packaging/porting to new platform">📦</a> <a href="https://github.com/eldang/elevation_lookups/pulls?q=is%3Apr+reviewed-by%3Adabreegster" title="Reviewed Pull Requests">👀</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!