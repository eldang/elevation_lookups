#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging
import os
import time

import geopandas as gp  # type: ignore
import requests

from shapely.geometry import box, LineString, Point  # type: ignore
from typing import List



class ElevationStats:

    def __init__(self) -> None:
        self.start: float = -1
        self.end: float = -1
        self.climb: float = -1
        self.descent: float = -1

    def __str__(self) -> str:
        return ", ".join([
            "Starting elevation: " + str(self.start),
            "Ending elevation: " + str(self.end),
            "Total climb: " + str(self.climb),
            "Total descent: " + str(self.descent)
        ])


class DataSource:

    def __init__(
        self,
        data_dir: str,
        data_source_list: str,
        bbox: box
    ) -> None:
        self.data_dir: str = data_dir
        self.sources_file: str = data_source_list

        self.__choose_source__(bbox)
        self.__download_file__()
        self.__read_file__(bbox)


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
                self.filetype: str = source["format"]
                self.source_crs: str = source["crs"]
                self.lookup_method: str = source["lookup_method"]
                self.lookup_field: str = source["lookup_field"]
                self.source_units: str = source["units"]
                self.recheck_days: int = source["recheck_interval_days"]
                logging.info('Using data source: %s %s', self.name, self.url)
                source_found = True
                break
            else:
                logging.debug(
                    ('Skipping data source "%s" because '
                        'it doesn`t cover the area needed.'),
                    source["name"]
                )
        if not source_found:
            logging.critical('No applicable data sources found.')
            exit(1)


    def __download_file__(self) -> None:
        # create or replace local file if appropriate
        file_needed: bool = False
        if not os.path.exists(self.filename):
            file_needed = True
            logging.info('Downloading data from %s', self.url)
        else:
            age: float = time.time() - os.stat(self.filename).st_mtime
            if age > self.recheck_days * 60 * 60 * 24:
                file_needed = True
                logging.info(
                    'Replacing %s from %s because it`s > than %s days old',
                    self.filename,
                    self.url,
                    self.recheck_days
                )
        if file_needed:
            req = requests.get(self.url)
            with open(self.filename, 'wb') as outfile:
                outfile.write(req.content)
        else:
            logging.info('Data file already saved at %s', self.filename)


    def __read_file__(self, bbox: box) -> None:
        # load this file to memory
        logging.info('Loading %s', self.filename)
        gdf = gp.read_file(self.filename)
        # limit to just the columns we need
        surplus_columns: List[str] = gdf.columns.tolist()
        surplus_columns.remove("geometry")
        surplus_columns.remove(self.lookup_field)
        gdf.drop(surplus_columns, axis=1, inplace=True)
        gdf.rename(columns={self.lookup_field: "elevation"}, inplace=True)
        # reproject if necessary
        if self.source_crs != 'EPSG:4326':
            logging.info('Reprojecting from %s to EPSG:4326', self.source_crs)
            gdf.to_crs(4326)
        # crop to bbox
        self.gdf = gp.clip(gdf, bbox, keep_geom_type=True)
        # convert units if necessary
        if self.source_units in ["feet", "foot", "ft"]:
            logging.info("Converting source elevations from feet to metres")
            self.gdf["elevation"] = self.gdf["elevation"] * 0.3048
        elif self.source_units not in ["meters", "metres", "m"]:
            logging.warning(
                ("Data source unit of '%s' not recognised; "
                    "using unconverted values"),
                self.source_units
            )


    def process(self, line: LineString) -> ElevationStats:
        stats = ElevationStats()
        stats.start = self.point_elevation(Point(line.coords[0]))
        stats.end = self.point_elevation(Point(line.coords[-1]))
        print(stats)
        return stats


    def point_elevation(self, point: Point) -> float:
        if self.lookup_method == "contour_lines":
            return self.nearest_contour(point)
        else:
            logging.critical(
                "Lookup method %s is not defined",
                self.lookup_method
            )
            exit(1)


    def nearest_contour(self, point: Point) -> float:
        clipped = gp.GeoDataFrame
        padding = 0.00001
        while clipped.empty or len(clipped.index) > 2:
            clipped = gp.clip(
                self.gdf, point.buffer(padding), keep_geom_type=True
            )
            if clipped.empty:
                padding = padding * 5
            else:
                padding = padding / 4
        return clipped["elevation"].mean()


    def __str__(self) -> str:
        return "DataSource " + str({
            "name": self.name,
            "local file": self.filename,
            "type": self.lookup_method,
            "CRS": self.source_crs,
            "elevation units": self.source_units
        })
