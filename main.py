#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Look up elevation data for a batch of paths

import logging
import os
import time

import click

__author__ = "Eldan Goldenberg for A/B Street, February-March 2021"
__license__ = "Apache"


@click.command()
@click.option(
    '--input_dir',
    default='input',
    help='Specify an input directory or leave out for default value: "input"'
)
@click.option(
    '--data_dir',
    default='data',
    help='Specify a data directory or leave out for default value: "data"'
)
@click.option(
    '--output_dir',
    default='output',
    help='Specify an output directory or leave out for default value: "output"'
)
@click.option(
    '--log',
    type=click.Choice(
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        case_sensitive=False
    ),
    default='INFO',
    help='Logging level.  Only messages of the selected severity or higher will be emitted.  Default: INFO'  # noqa: E501
)
@click.argument('input_file')
def main(
    input_dir: str,
    data_dir: str,
    output_dir: str,
    input_file: str,
    log: str
) -> None:
    start_time: float = time.time()
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:\t%(message)s',
        datefmt='%Y%m%d %H:%M',
        level=log
    )
    logging.debug("Starting run")
    n_rows: int = 0
    with open(os.path.join(input_dir, input_file)) as infile:
        for row in infile:
            n_rows += 1
    logging.info("read %s rows", n_rows)
    logging.info("Run complete in %s.", elapsedTime(start_time))





def elapsedTime(start_time: float) -> str:
    seconds: float = time.time() - start_time
    if seconds < 1:
        return "less than one second"
    hours: int = int(seconds / 60 / 60)
    minutes: int = int(seconds / 60 - hours * 60)
    seconds: int = int(seconds - minutes * 60 - hours * 60 * 60)
    if minutes < 1 and hours < 1:
        return str(seconds) + " seconds"
    elif hours < 1:
        return str(minutes) + " minute[s] and " + str(seconds) + " second[s]"
    else:
        return (
            str(hours) + " hour[s], " +
            str(minutes) + " minute[s] and " +
            str(seconds) + " second[s]"
        )



if __name__ == "__main__":
    main()
