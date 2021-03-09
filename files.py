#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file handlers and objects

import logging
import os
from shapely.geometry import LineString, MultiLineString # type: ignore
from typing import List, Tuple


class InputFile:

    def __init__(self, input_dir: str, input_file: str) -> None:
        self.file_path: str = os.path.join(input_dir, input_file)
        self.n_rows: int = 0

        lines: List[LineString] = []
        with open(self.file_path) as f:
            for row in f:
                self.n_rows += 1
                lines.append(self.__buildLine__(row))
        self.paths = MultiLineString(lines)
        logging.info("Found %s rows in %s", self.n_rows, self.file_path)
        logging.info("Area covered: %s", self.paths.bounds)

    def __buildLine__(self, raw_line) -> LineString:
        coords: List[Tuple[float, float]] = []
        for point in raw_line.split(" "):
            vals = [float(x) for x in point.split(",")]
            coords.append((vals[0], vals[1]))
        return LineString(coords)
