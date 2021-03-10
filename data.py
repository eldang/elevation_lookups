#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging
import os
import requests
import time

from shapely.geometry import box  # type: ignore
from typing import Tuple



class DataSource:

    def __init__(
        self,
        data_dir: str,
        data_source_list: str,
        bbox: Tuple[float, float, float, float]
    ) -> None:
        self.data_dir: str = data_dir
        self.sources_file: str = data_source_list
        source_found: bool = False

        with open(self.sources_file) as infile:
            sources = json.load(infile)["sources"]

        for source in sources:
            if box(*source["bbox"]).contains(box(*bbox)):
                self.name: str = source["name"]
                self.url: str = source["url"]
                self.filename: str = os.path.join(data_dir, source["filename"])
                self.filetype: str = source["format"]
                self.lookup_method: str = source["lookup_method"]
                self.recheck_interval: int = source["recheck_interval"]
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
            exit(-1)

        file_needed: bool = False
        if not os.path.exists(self.filename):
            file_needed = True
            logging.info('Downloading data from %s', self.url)
        else:
            timestamp: float = os.stat(self.filename).st_mtime
            if time.time() - timestamp > self.recheck_interval * 60 * 60 * 24:
                file_needed = True
                logging.info(
                    'Replacing %s from %s because it`s > than %s days old',
                    self.filename,
                    self.url,
                    self.recheck_interval
                )

        if file_needed:
            req = requests.get(self.url)
            with open(self.filename, 'wb') as outfile:
                outfile.write(req.content)
        else:
            logging.info('Data file already saved at %s', self.filename)


    def __str__(self) -> str:
        return self.name
