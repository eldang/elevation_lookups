#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data source management

import json
import logging

from shapely.geometry import box
from typing import Dict, List, Tuple  # type: ignore


class DataSource:

    def __init__(self, source_info: Dict) -> None:
        logging.debug(source_info)
        self.name: str = source_info["name"]
        self.url: str = source_info["url"]
        self.filename: str = source_info["filename"]
        self.filetype: str = source_info["format"]
        self.lookup_method: str = source_info["lookup_method"]
        self.recheck_interval: int = source_info["recheck_interval"]

    def __str__(self) -> str:
        return self.name



class DataSources:

    def __init__(
        self,
        data_dir: str,
        data_source_list: str,
        bbox: Tuple[float, float, float, float]
    ) -> None:
        self.data_dir: str = data_dir
        self.sources_file: str = data_source_list
        self.sources: List[DataSource] = []

        with open(self.sources_file) as f:
            self.source_info = json.load(f)["sources"]

        for source in self.source_info:
            if box(*source["bbox"]).contains(box(*bbox)):
                self.sources.append(DataSource(source))
            else:
                logging.debug(
                    ('Skipping data source %s because '
                        'it doesn`t cover the area needed.'),
                    source["name"]
                )

    def __str__(self) -> str:
        return str([str(x) for x in self.sources])
