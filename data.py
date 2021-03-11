#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging
import os
import pyproj
import requests
import time

from shapely.geometry import box, LineString  # type: ignore
from shapely.ops import transform  # type: ignore
from typing import Any, List, Tuple



class DataSource:

    def __init__(
        self,
        data_dir: str,
        data_source_list: str,
        bbox: Tuple[float, float, float, float]
    ) -> None:
        self.data_dir: str = data_dir
        self.sources_file: str = data_source_list

        # load available sources from metadata JSON
        with open(self.sources_file) as infile:
            sources = json.load(infile)["sources"]

        # try to find an applicable source; quit if none found
        source_found: bool = False
        for source in sources:
            if box(*source["bbox"]).contains(box(*bbox)):
                self.name: str = source["name"]
                self.url: str = source["url"]
                self.filename: str = os.path.join(data_dir, source["filename"])
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

        # load this file to the class
        logging.info('Reading %s as %s', self.filename, self.filetype)
        raw_features: List[Tuple[List[float], float]]  # [([[x,y]], elevation)]
        if self.filetype == "geojson":
            with open(self.filename) as infile:
                raw_features = [
                    (
                        x["geometry"]["coordinates"],
                        x["properties"][self.lookup_field]
                    ) for x in json.load(infile)["features"]
                ]
        else:
            logging.critical('File type %s not supported', self.filetype)
            exit(1)
        print(len(raw_features))
        logging.info('Parsing %s as %s', self.filename, self.lookup_method)
        reprojector = pyproj.Transformer.from_crs(
            pyproj.CRS(self.source_crs),
            pyproj.CRS('EPSG:4326'),
            always_xy=True
        ).transform
        self.features: List[Tuple[Any, float]] = []  # [(shape, elevation)]
        if self.lookup_method == "contour_lines":
            for feature in raw_features:
                line = LineString(feature[0])
                if line.intersects(box(*bbox)):
                    if self.source_crs == 'EPSG:4326':
                        self.features.append((line, feature[1]))
                    else:
                        self.features.append(
                            (transform(reprojector, line), feature[1])
                        )
        else:
            logging.critical(
                'Lookup method %s not supported', self.lookup_method
            )
            exit(1)
        print(len(self.features))


    def __str__(self) -> str:
        return str([
            self.name,
            self.filename,
            self.filetype,
            self.lookup_method,
            self.source_crs,
            self.source_units
        ])
