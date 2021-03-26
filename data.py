#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging
import math
import multiprocessing as mp
import os
import time
import urllib.request as ftp
import warnings

import elevation as eio  # type: ignore
# elevation is an SRTM downloader.  See https://github.com/bopen/elevation
import fiona  # type: ignore  # noqa: F401
# fiona is only used indirectly, but needs to be explicitly imported to avoid:
# ` AttributeError: partially initialized module 'fiona' has no
# attribute '_loading' (most likely due to a circular import) `
import geopandas as gp  # type: ignore
import pyproj
import rasterio  # type: ignore
import rasterio.merge  # type: ignore
import requests

from shapely.geometry import box, LineString, MultiLineString, Point  # type: ignore  # noqa: E501
from shapely.ops import transform  # type: ignore
from typing import List


SCREEN_PRECISION: int = 2  # round terminal output to 1cm
FOOT_IN_M: float = 0.3048
NULL_ELEVATION: float = -11000  # deeper than the deepest ocean




class ElevationStats:

    def __init__(self, i: int = -1) -> None:
        self.i: int = i
        self.start: float = NULL_ELEVATION
        self.end: float = NULL_ELEVATION
        self.climb: float = 0
        self.descent: float = 0

    def __str__(self) -> str:
        return " \t".join([
            'row: ' + str(self.i),
            'Starting elevation: ' +
            str(round(self.start, SCREEN_PRECISION)),
            'Ending elevation: ' +
            str(round(self.end, SCREEN_PRECISION)),
            'Total climb: ' +
            str(round(self.climb, SCREEN_PRECISION)),
            'Total descent: ' +
            str(round(self.descent, SCREEN_PRECISION))
        ])



class DataSource:

    def __init__(
        self,
        logger_name: str,
        data_dir: str,
        data_source_list: str,
        bbox: box
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self.data_dir: str = data_dir
        self.sources_file: str = data_source_list

        self.__choose_source__(bbox)
        if self.lookup_method == "contour_lines":
            self.__read_vectors__(bbox)
        elif self.lookup_method != "raster":
            self.logger.critical(
                "Lookup method %s not implemented",
                self.lookup_method
            )
            exit(1)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


    def __choose_source__(self, bbox: box) -> None:
        # load available sources from metadata JSON
        with open(self.sources_file) as infile:
            sources = json.load(infile)["sources"]

        # try to find an applicable source
        for source in sources:
            if box(*source["bbox"]).contains(bbox):
                self.name: str = source["name"]
                self.url: str = source["url"]
                self.filename: str = os.path.join(
                    self.data_dir, source["filename"]
                )
                self.source_crs: str = source["crs"]
                self.download_method: str = source["download_method"]
                self.lookup_method: str = source["lookup_method"]
                self.lookup_field: str = source["lookup_field"]
                self.source_units: str = source["units"]
                self.recheck_days: int = source["recheck_interval_days"]
                self.logger.info('Using data source: %s', self.name)
                self.__download_file__(bbox)
                return
            else:
                self.logger.debug(
                    ('Skipping data source "%s" because '
                        'it doesn`t cover the area needed.'),
                    source["name"]
                )
        # fall back to SRTM if no preferred source found
        self.logger.info(
            'No applicable data sources found in %s, defaulting to SRTM.',
            self.sources_file
        )
        self.name = "SRTM 30m"
        self.url = "https://lpdaac.usgs.gov/products/srtmgl1nv003/"
        self.filename = os.path.join(os.getcwd(), self.data_dir, "srtm")
        if not os.path.exists(self.filename):
            os.mkdir(self.filename)
        self.source_crs = "EPSG:4326"
        self.download_method = "srtm"
        self.lookup_method = "raster"
        self.lookup_field = "1"
        self.source_units = "meters"
        self.recheck_days = 100
        self.__download_srtm__(bbox)


    def __download_file__(self, bbox: box) -> None:
        # create or replace local file if appropriate
        file_needed: bool = False
        if not os.path.exists(self.filename):
            file_needed = True
        elif self.download_method != "local" and self.recheck_days is not None:
            age: float = time.time() - os.stat(self.filename).st_mtime
            if age > self.recheck_days * 60 * 60 * 24:
                file_needed = True
                self.logger.info(
                    'Replacing %s from %s because it`s > than %s days old',
                    self.filename,
                    self.url,
                    self.recheck_days
                )
        if file_needed:
            if self.download_method == "http":
                self.logger.info('Downloading %s as http', self.url)
                req = requests.get(self.url)
                with open(self.filename, 'wb') as outfile:
                    outfile.write(req.content)
            elif self.download_method == "ftp":
                self.logger.info('Downloading %s as ftp', self.url)
                ftp.urlretrieve(self.url, self.filename)
            elif self.download_method == "local":
                self.logger.critical(
                    'Local file %s not found.',
                    self.filename
                )
                exit(1)
            else:
                self.logger.critical(
                    'Download method %s not supported',
                    self.download_method
                )
                exit(1)
        else:
            self.logger.info('Data file already saved at %s', self.filename)


    def __download_srtm__(self, bbox: box) -> None:
        # make a list of file[s] needed
        tiles: List[int] = [
            math.floor(bbox.bounds[0]),
            math.floor(bbox.bounds[1]),
            math.ceil(bbox.bounds[2]),
            math.ceil(bbox.bounds[3]),
        ]
        self.srtm_tiles: List[str] = []
        for x in range(tiles[0], tiles[2]):
            for y in range(tiles[1], tiles[3]):
                self.srtm_tiles.append(os.path.join(
                    self.filename,
                    "srtm." + str(x) + "." + str(y) + ".tif"
                ))
        # download file[s] if appropriate
        for filename in self.srtm_tiles:
            file_needed: bool = True
            if os.path.exists(filename):
                age: float = time.time() - os.stat(filename).st_mtime
                if age > self.recheck_days * 60 * 60 * 24:
                    self.logger.info(
                        'Replacing %s because it`s > than %s days old',
                        filename,
                        self.recheck_days
                    )
                else:
                    file_needed = False
                    self.logger.info('Tile already saved at %s', filename)
            else:
                self.logger.info('Downloading %s', filename)
            if file_needed:
                eio.clip(bounds=[x, y, x + 1, y + 1], output=filename)
        # merge files to temp.....tif on disk
        tile_id: str = str(tiles[0]) + "_" + str(tiles[1])
        tile_id += "_" + str(tiles[2]) + "_" + str(tiles[3])
        self.filename = os.path.join(
            self.filename,
            "temp_" + tile_id + "_" + str(time.time()) + ".tif"
        )
        self.logger.info(
            'Saving SRTM data cropped to %s as %s',
            bbox.bounds,
            self.filename
        )
        rasterio.merge.merge(
            self.srtm_tiles,
            bounds=bbox.bounds,
            dst_path=self.filename
        )


    def __read_vectors__(self, bbox: box) -> None:
        self.logger.info('Loading %s as vector data', self.filename)
        gdf = gp.read_file(self.filename)
        # reproject if necessary
        if self.source_crs != 'EPSG:4326':
            self.logger.info(
                'Reprojecting from %s to EPSG:4326',
                self.source_crs
            )
            gdf.to_crs(4326)
        # crop to bbox and standardise fields
        self.logger.info('Cropping to %s', bbox.bounds)
        self.gdf = gdf.loc[
            gdf.sindex.query(bbox),
            ["geometry", self.lookup_field]
        ]
        self.gdf.rename(columns={self.lookup_field: "elevation"}, inplace=True)
        # convert units if necessary
        if self.source_units in ["feet", "foot", "ft"]:
            self.logger.info(
                "Converting source elevations from feet to metres"
            )
            self.gdf["elevation"] = self.gdf["elevation"] * FOOT_IN_M
        elif self.source_units not in ["meters", "metres", "m"]:
            self.logger.warning(
                ("Data source unit of '%s' not recognised; "
                    "using unconverted values"),
                self.source_units
            )


    def __read_raster__(self, bbox: box) -> None:
        self.raster_dataset = rasterio.open(self.filename)
        self.raster_values = self.raster_dataset.read(int(self.lookup_field))
        # instead of reprojecting a raster,
        # configure a reprojector for queries to it
        if self.source_crs != "EPSG:4326":
            self.reprojector = pyproj.Transformer.from_crs(
                crs_from=pyproj.CRS("EPSG:4326"),
                crs_to=pyproj.CRS(self.source_crs),
                always_xy=True
            ).transform


    def tag_multiline(
        self,
        lines: MultiLineString,
        n_threads: int
    ) -> List[ElevationStats]:
        vals: List[ElevationStats] = []
        # allow multiprocessing to be sidestepped so there's always an
        # option for simple, sequential runs for debugging purposes
        if n_threads == 1:
            self.logger.info('Processing singlethreaded.')
            if self.lookup_method == "contour_lines":
                self.logger.info("Creating spatial index")
                self.idx = self.gdf.sindex
                self.logger.info("Deriving elevations from contours")
                for i in range(len(lines)):
                    vals.append(self.__contour_line_crossings__(
                        lines[i], i)
                    )
            elif self.lookup_method == "raster":
                self.logger.info('Loading %s as raster data', self.filename)
                self.__read_raster__(box(*lines.bounds))
                for i in range(len(lines)):
                    vals.append(self.__raster_line_lookups__(lines[i], i))
                self.raster_dataset.close()
            return vals
        else:
            self.logger.info('Spawning %s threads', n_threads)
            q: mp.JoinableQueue = mp.JoinableQueue()  # for processing
            out: mp.Queue = mp.Queue()  # to collect output
            # put each line into the queue
            for i in range(len(lines)):
                q.put({
                    "line": lines[i],
                    "i": i
                })
            # start an appropriate number of workers
            for i in range(n_threads):
                self.logger.debug("Spawning thread %s", i)
                if self.lookup_method == "contour_lines":
                    mp.Process(
                        target=self.__parallel_contour_worker__,
                        args=(q, out, i, self.logger.getEffectiveLevel())
                    ).start()
                elif self.lookup_method == "raster":
                    mp.Process(
                        target=self.__parallel_raster_worker__,
                        args=(
                            q,
                            out,
                            box(*lines.bounds),
                            i,
                            self.logger.getEffectiveLevel()
                        )
                    ).start()
            q.join()
            self.logger.debug("Parallel processing complete")
            # collect all the output into one list
            while not out.empty():
                vals.append(out.get())
            # output order is not guaranteed, so sort it on returning
            return sorted(vals, key=lambda x: x.i)


    def __parallel_contour_worker__(
        self,
        q: mp.JoinableQueue,
        out: mp.Queue,
        i: int,
        loglevel: int
    ) -> None:
        jobcount: int = 0
        # taking a shortcut because the built-in logging
        # becomes tricky with multiprocessing
        if loglevel < logging.INFO:
            print("Thread " + str(i) + " creating spatial index")
        # spatial indexes can't be passed to child processes,
        # so make one in each thread.  Fortunately, this is a quick operation.
        self.idx = self.gdf.sindex
        if loglevel < logging.INFO:
            print("Thread " + str(i) + " deriving elevations from contours")
        while not q.empty():
            job = q.get()
            out.put(self.__contour_line_crossings__(job["line"], job["i"]))
            q.task_done()
            jobcount += 1
        if loglevel <= logging.INFO:
            print(
                "Thread " + str(i) + " processed " + str(jobcount) + " lines"
            )


    def __parallel_raster_worker__(
        self,
        q: mp.JoinableQueue,
        out: mp.Queue,
        bbox: box,
        i: int,
        loglevel: int
    ) -> None:
        jobcount: int = 0
        # taking a shortcut because the built-in logging
        # becomes tricky with multiprocessing
        if loglevel < logging.INFO:
            print(
                "Thread " + str(i) + " loading " + self.filename + " as raster"
            )
        # rasterio datasets can't be passed to child threads, so repeat the
        # load in each thread.  Fortunately, this is a quick operation.
        self.__read_raster__(bbox)
        if loglevel < logging.INFO:
            print("Thread " + str(i) + " deriving elevations from raster")
        while not q.empty():
            job = q.get()
            out.put(self.__raster_line_lookups__(job["line"], job["i"]))
            q.task_done()
            jobcount += 1
        if loglevel <= logging.INFO:
            print(
                "Thread " + str(i) + " processed " + str(jobcount) + " lines"
            )
        self.raster_dataset.close()


    def __nearest_contour__(self, point: Point) -> float:
        # Check for intersections with progressively larger
        # buffers until we find at least one contour
        subset: List[int] = []
        padding: float = 0.00001
        i: int = 0
        while len(subset) < 1:
            i += 1
            subset = self.idx.query(
                point.buffer(padding * i), predicate="intersects"
            )
        # if we have exactly one result, it must be the nearest
        if len(subset) == 1:
            return self.gdf.elevation.iloc[subset[0]]
        # otherwise calculate distances among the subset returned by .query
        with warnings.catch_warnings():
            # suppressing the geopandas UserWarning about distances from a
            # projected CRS, because we only care about _relative_ distance
            warnings.simplefilter(action='ignore', category=UserWarning)
            distances = self.gdf.iloc[subset].distance(point)
        # and return the elevation of the closest contour
        return self.gdf.loc[distances.idxmin()]["elevation"]


    def __contour_line_crossings__(
        self,
        line: LineString,
        i: int
    ) -> ElevationStats:
        stats = ElevationStats(i)
        # Find the elevation of the first point
        stats.start = self.__nearest_contour__(Point(line.coords[0]))
        # if we only have one point then we're set
        if (len(line.coords) == 1) or (
            (len(line.coords) == 2) and (line.coords[0] == line.coords[-1])
        ):
            stats.end = stats.start
        # otherwise find all the contour crossings to get the total
        else:
            previous_elevation: float = stats.start
            for coord in line.coords[1:]:
                elevation: float = self.__nearest_contour__(Point(coord))
                if elevation > previous_elevation:
                    stats.climb += elevation - previous_elevation
                elif elevation < previous_elevation:
                    stats.descent += previous_elevation - elevation
                previous_elevation = elevation
            # after the loop, we already have our final elevation
            stats.end = elevation
        return stats


    def __raster_point_lookup__(self, point: Point) -> float:
        if self.source_crs == "EPSG:4326":
            row, col = self.raster_dataset.index(point.x, point.y)
        else:
            projected = transform(self.reprojector, point)
            row, col = self.raster_dataset.index(projected.x, projected.y)
        return self.raster_values[row, col]


    def __raster_line_lookups__(
        self,
        line: LineString,
        i: int
    ) -> ElevationStats:
        stats = ElevationStats(i)
        # Find the elevation of the first point
        stats.start = self.__raster_point_lookup__(Point(line.coords[0]))
        # deal with nodata returns
        while stats.start <= NULL_ELEVATION:
            if len(line.coords) <= 1:
                return ElevationStats()
            line.coords = line.coords[1:]
            stats.start = self.__raster_point_lookup__(
                Point(line.coords[0])
            )
        # if we only have one point then we're set
        if (len(line.coords) == 1) or (
            (len(line.coords) == 2) and (line.coords[0] == line.coords[-1])
        ):
            stats.end = stats.start
        # otherwise find all the contour crossings to get the total
        else:
            previous_elevation: float = stats.start
            for coord in line.coords[1:]:
                elevation: float = self.__raster_point_lookup__(Point(coord))
                if elevation > NULL_ELEVATION:
                    if elevation > previous_elevation:
                        stats.climb += elevation - previous_elevation
                    elif elevation < previous_elevation:
                        stats.descent += previous_elevation - elevation
                    previous_elevation = elevation
            # after the loop, we already have our final elevation
            stats.end = elevation
        return stats


    def close(self) -> None:
        if self.download_method == "srtm":
            self.logger.info('Removing temp data file %s', self.filename)
            os.remove(self.filename)


    def __str__(self) -> str:
        return "DataSource " + str({
            "name": self.name,
            "local file": self.filename,
            "type": self.lookup_method,
            "CRS": self.source_crs,
            "elevation units": self.source_units
        })
