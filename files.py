#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# file handlers and objects

import logging
import os



class InputFile:
    n_rows: int = 0

    def __init__(self, input_dir: str, input_file: str):
        with open(os.path.join(input_dir, input_file)) as f:
            print(type(f))
            for row in f:
                self.n_rows += 1
        logging.info("read %s rows", self.n_rows)
