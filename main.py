#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Look up elevation data for a batch of paths

import logging
import sys
import time


__author__ = "Eldan Goldenberg for A/B Street, February-March 2021"
__license__ = "Apache"



def main():
    start_time = time.time()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y%m%d %H:%M', level="INFO")
    logging.debug("Starting run")
    logging.info("Run complete in %s.", elapsedTime(start_time))





def elapsedTime(start_time):
    seconds = time.time() - start_time
    if seconds < 1:
        return "less than one second"
    hours = int(seconds / 60 / 60)
    minutes = int(seconds / 60 - hours * 60)
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
    try:
        main()
    except:  # noqa: E722
        logging.error(sys.exc_info()[0])
        import traceback
        logging.error(traceback.format_exc())
