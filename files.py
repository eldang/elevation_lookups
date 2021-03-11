#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file handlers and objects

import logging
import os
from shapely.geometry import box, LineString, MultiLineString  # type: ignore
from typing import List, Tuple


class InputFile:

    def __init__(self, input_dir: str, input_file: str) -> None:
        self.file_path: str = os.path.join(input_dir, input_file)

        lines: List[LineString] = []
        with open(self.file_path) as f:
            for row in f:
                lines.append(self.__build_line__(row))
        self.__paths = MultiLineString(lines)
        logging.info("Found %s rows in %s", self.n_lines(), self.file_path)
        logging.info("Area covered: %s", self.bbox())

    def __build_line__(self, raw_line) -> LineString:
        coords: List[Tuple[float, float]] = []
        for point in raw_line.split(" "):
            vals = [float(x) for x in point.split(",")]
            coords.append((vals[0], vals[1]))
        return LineString(coords)

    def bbox(self) -> box:
        return box(*self.__paths.bounds)

    def n_lines(self) -> int:
        return len(self.__paths.geoms)
