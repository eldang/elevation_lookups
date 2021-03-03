#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file handlers and objects

import logging
import os
from typing import Dict, List



class InputFile:

    def __init__(self, input_dir: str, input_file: str):
        self.file_path: str = os.path.join(input_dir, input_file)
        self.n_rows: int = 0
        with open(self.file_path) as f:
            for row in f:
                self.n_rows += 1
                poly_line = PolyLine(row)
                logging.info(poly_line.bbox)
        logging.info("read %s rows", self.n_rows)


class PolyLine:

    def __init__(self, raw_row: str):
        self.coords: List[Dict[str, float]] = []
        self.bbox: Dict[str, float] = {}
        for point in raw_row.split(" "):
            vals = point.split(",")
            self.coords.append({
                'x': float(vals[0]),
                'y': float(vals[1])
            })
        self.bbox = {
            'W': self.coords[0]['x'],
            'S': self.coords[0]['y'],
            'E': self.coords[0]['x'],
            'N': self.coords[0]['y']
        }
        for coord in self.coords[1:]:
            if coord['x'] < self.bbox['W']:
                self.bbox['W'] = coord['x']
            if coord['y'] < self.bbox['S']:
                self.bbox['S'] = coord['y']
            if coord['x'] > self.bbox['E']:
                self.bbox['E'] = coord['x']
            if coord['y'] > self.bbox['N']:
                self.bbox['N'] = coord['y']
