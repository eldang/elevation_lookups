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
3. Possibly also steepest segment characterisation, for unevenly steep blocks.

I'm also doing some research on what existing bike routefinding packages use.

## Roughly sketched out design

1. Store local copies of data sources, at least for the areas that we're actively building models for.
2. On startup, look for missing or potentially stale data and download/replace as appropriate.
3. While running, serve a simple [REST? that seems like the way to go] API that can be queried with individual points to get their elevation, or a pair of points to get the elevation gain from 1 to 2.  Leave it to the querying process to calculate gradients.  For a pair of points, return the two elevations and the total climb between them, *which may be more than the delta*.
4. When queried, use more local data if available, falling back to SRTM when none is.
5. Extra credit: where multiple data sources are available, is it useful to have the API check more than one and warn about discrepancies?
