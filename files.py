#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file handlers and objects

import logging
import os
from typing import Dict, List

from data import BoundingBox


class InputFile:

    def __init__(self, input_dir: str, input_file: str) -> None:
        self.file_path: str = os.path.join(input_dir, input_file)
        self.n_rows: int = 0
        self.bbox = BoundingBox()

        with open(self.file_path) as f:
            for row in f:
                self.n_rows += 1
                poly_line = PolyLine(row)
                if self.bbox.empty:
                    self.bbox = poly_line.getBbox()
                else:
                    bbox: BoundingBox = poly_line.getBbox()
                    if bbox.W is not None and bbox.W < self.bbox.W:
                        self.bbox.W = bbox.W
                    if bbox.S < self.bbox.S:
                        self.bbox.S = bbox.S
                    if bbox.E > self.bbox.E:
                        self.bbox.E = bbox.E
                    if bbox.N > self.bbox.N:
                        self.bbox.N = bbox.N
        logging.info("Found %s rows in %s", self.n_rows, self.file_path)
        logging.info("Area covered: %s", self.bbox)




class PolyLine:

    def __init__(self, raw_row: str) -> None:
        self.coords: List[Dict[str, float]] = []
        self.bbox = BoundingBox()

        for point in raw_row.split(" "):
            vals = point.split(",")
            self.coords.append({
                'x': float(vals[0]),
                'y': float(vals[1])
            })

    def getBbox(self) -> BoundingBox:
        if self.bbox.empty:
            self.bbox = BoundingBox(
                self.coords[0]['x'],
                self.coords[0]['y'],
                self.coords[0]['x'],
                self.coords[0]['y']
            )

            for coord in self.coords[1:]:
                if coord['x'] < self.bbox.W:
                    self.bbox.W = coord['x']
                if coord['y'] < self.bbox.S:
                    self.bbox.S = coord['y']
                if coord['x'] > self.bbox.E:
                    self.bbox.E = coord['x']
                if coord['y'] > self.bbox.N:
                    self.bbox.N = coord['y']
        return self.bbox
