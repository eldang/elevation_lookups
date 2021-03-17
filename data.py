#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging
import os
import time
import warnings

import elevation as eio  # type: ignore
# elevation is an SRTM downloader.  See https://github.com/bopen/elevation
import geopandas as gp  # type: ignore
import rasterio  # type: ignore
import requests

from shapely.geometry import box, LineString, Point  # type: ignore
from typing import List


SCREEN_PRECISION: int = 2  # round terminal output to 1cm
FOOT_IN_M: float = 0.3048
NULL_ELEVATION: float = -11000  # deeper than the deepest ocean


class ElevationStats:

    def __init__(self) -> None:
        self.start: float = NULL_ELEVATION
        self.end: float = NULL_ELEVATION
        self.climb: float = 0
        self.descent: float = 0

    def __str__(self) -> str:
        return " \t".join([
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
        self.__download_file__(bbox)
        if self.lookup_method == "contour_lines":
            self.__read_vectors__(bbox)
        elif self.lookup_method == "raster":
            self.__read_raster__(bbox)
        else:
            self.logger.critical(
                "Lookup method %s not implemented",
                self.lookup_method
            )
            exit(1)


    def __choose_source__(self, bbox: box) -> None:
        # load available sources from metadata JSON
        with open(self.sources_file) as infile:
            sources = json.load(infile)["sources"]

        # try to find an applicable source; quit if none found
        source_found: bool = False
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
                self.logger.info(
                    'Using data source: %s %s',
                    self.name,
                    self.url
                )
                source_found = True
                break
            else:
                self.logger.debug(
                    ('Skipping data source "%s" because '
                        'it doesn`t cover the area needed.'),
                    source["name"]
                )
        if not source_found:
            self.logger.critical('No applicable data sources found.')
            exit(1)


    def __download_file__(self, bbox: box) -> None:
        # create or replace local file if appropriate
        file_needed: bool = False
        if not os.path.exists(self.filename):
            file_needed = True
            self.logger.info('Downloading data from %s', self.url)
        else:
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
            if self.download_method == "url":
                req = requests.get(self.url)
                with open(self.filename, 'wb') as outfile:
                    outfile.write(req.content)
            elif self.download_method == "srtm":
                eio.clip(
                    bounds=bbox.bounds,
                    output=os.path.join(os.getcwd(), self.filename)
                )
            else:
                self.logger.critical(
                    'Download method %s not supported',
                    self.download_method
                )
                exit(1)
        else:
            self.logger.info('Data file already saved at %s', self.filename)


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
        self.logger.info(
            'Cropping to %s',
            [bbox.exterior.coords[0], bbox.exterior.coords[2]]
        )
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
        self.logger.info("Creating spatial index")
        self.idx = self.gdf.sindex


    def __read_raster__(self, bbox: box) -> None:
        self.logger.info('Loading %s as raster data', self.filename)
        with rasterio.open(self.filename) as src:
            self.raster = src.read()


    def process(self, line: LineString) -> ElevationStats:
        if self.lookup_method == "contour_lines":
            return self.__contour_line_crossings__(line)
        else:
            self.logger.critical(
                "Lookup method %s is not defined",
                self.lookup_method
            )
            exit(1)


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


    def __contour_line_crossings__(self, line: LineString) -> ElevationStats:
        stats = ElevationStats()
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


    def __str__(self) -> str:
        return "DataSource " + str({
            "name": self.name,
            "local file": self.filename,
            "type": self.lookup_method,
            "CRS": self.source_crs,
            "elevation units": self.source_units
        })
