#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging
import os
import time

import geopandas as gp  # type: ignore
import requests

from shapely.geometry import box  # type: ignore
from typing import List, Tuple



class DataSource:

    def __init__(
        self,
        data_dir: str,
        data_source_list: str,
        bbox: Tuple[float, float, float, float]
    ) -> None:
        self.data_dir: str = data_dir
        self.sources_file: str = data_source_list

        self.choose_source(bbox)
        self.download_file()
        self.read_file(bbox)


    def choose_source(self, bbox: Tuple[float, float, float, float]) -> None:
        # load available sources from metadata JSON
        with open(self.sources_file) as infile:
            sources = json.load(infile)["sources"]

        # try to find an applicable source; quit if none found
        source_found: bool = False
        for source in sources:
            if box(*source["bbox"]).contains(box(*bbox)):
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


    def download_file(self) -> None:
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


    def read_file(self, bbox: Tuple[float, float, float, float]) -> None:
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
        self.gdf = gp.clip(gdf, box(*bbox), keep_geom_type=True)
        print(self.gdf.head())


    def __str__(self) -> str:
        return str([
            self.name,
            self.filename,
            self.filetype,
            self.lookup_method,
            self.source_crs,
            self.source_units
        ])
