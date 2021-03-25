#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file handlers and objects

import logging
import os
from typing import List, Tuple

from shapely.geometry import box, LineString, MultiLineString  # type: ignore

from data import DataSource, ElevationStats, NULL_ELEVATION



SAVE_PRECISION: int = 3  # round values to mm in the saved output


class OutputFile:

    def __init__(
        self,
        logger_name: str,
        output_dir: str,
        output_file: str
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self.file_path: str = os.path.join(output_dir, output_file)

        if os.path.exists(self.file_path):
            self.logger.info("Overwriting existing %s", self.file_path)
        else:
            self.logger.info("Creating output file %s", self.file_path)

        self.f = open(self.file_path, 'w')

    def write_elevations(self, data: ElevationStats) -> None:
        # skip NULL returns
        if data.start != NULL_ELEVATION and data.end != NULL_ELEVATION:
            self.f.write(str(round(data.start, SAVE_PRECISION)))
            self.f.write('\t')
            self.f.write(str(round(data.end, SAVE_PRECISION)))
            self.f.write('\t')
            self.f.write(str(round(data.climb, SAVE_PRECISION)))
            self.f.write('\t')
            self.f.write(str(round(data.descent, SAVE_PRECISION)))
        self.f.write('\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self) -> None:
        self.f.close()

    def __str__(self) -> str:
        return self.file_path



class InputFile:

    def __init__(
        self,
        logger_name: str,
        input_dir: str,
        input_file: str
    ) -> None:
        self.logger = logging.getLogger(logger_name)
        self.file_path: str = os.path.join(input_dir, input_file)

        lines: List[LineString] = []
        with open(self.file_path) as f:
            for row in f:
                lines.append(self.__build_line__(row))
        self.__paths = MultiLineString(lines)
        self.logger.info("Found %s rows in %s", self.n_lines(), self.file_path)
        self.logger.info("Area covered: %s", self.__paths.bounds)

    def __build_line__(self, raw_line) -> LineString:
        coords: List[Tuple[float, float]] = []
        for point in raw_line.split(" "):
            vals = [float(x) for x in point.split(",")]
            coords.append((vals[0], vals[1]))
        return LineString(coords)

    def process(
        self,
        d: DataSource,
        outfile: OutputFile,
        n_threads: int
    ) -> None:
        self.logger.debug('Processing with %s threads', n_threads)
        for line in self.__paths:
            vals: ElevationStats = d.process(line)
            outfile.write_elevations(vals)

    def bbox(self) -> box:
        return box(*self.__paths.bounds)

    def n_lines(self) -> int:
        return len(self.__paths.geoms)
