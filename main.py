#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Look up elevation data for a batch of paths

import logging
import sys
import time

import click

from data import DataSource
from files import InputFile, OutputFile

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
    '--data_source_list',
    default='datasources.json',
    help=('Path to a JSON file enumerating available data sources, '
            'or leave out for default value: "datasources.json"')
)
@click.option(
    '--n_threads',
    default=5,
    help=('Number of threads to execute in parallel, '
            'or leave out for default value: 5')  # noqa: E127
)
@click.option(
    '--log',
    type=click.Choice(
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    ),
    default='INFO',
    help=('Logging level.  '
            'Only messages of the selected severity or higher will be emitted.'
            'Default: INFO')
)
@click.argument('input_file')
def main(
    input_dir: str,
    data_dir: str,
    output_dir: str,
    data_source_list: str,
    input_file: str,
    n_threads: int,
    log: str
) -> None:
    start_time: float = time.time()
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:\t%(message)s',
        datefmt='%Y%m%d %H:%M'
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(level=log)
    logger.debug("Starting run")
    infile = InputFile(__name__, input_dir, input_file)
    with DataSource(__name__, data_dir, data_source_list, infile.bbox()) as d:
        with OutputFile(__name__, output_dir, input_file) as outfile:
            infile.tag_elevations(d, outfile, n_threads)
    logger.info("Run complete in %s.", elapsedTime(start_time))
    sys.exit(0)





def elapsedTime(start_time: float) -> str:
    seconds: float = time.time() - start_time
    if seconds < 1:
        return "less than one second"
    hours: int = int(seconds / 60 / 60)
    minutes: int = int(seconds / 60 - hours * 60)
    seconds = int(seconds - minutes * 60 - hours * 60 * 60)
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
