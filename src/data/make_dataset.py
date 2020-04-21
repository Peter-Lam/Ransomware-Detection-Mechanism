#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    This is the main file to making the dataset.
    This will download data, create the raw data and preprocces it.
'''
import logging
import time
import click
# from pathlib import Path
# from dotenv import find_dotenv, load_dotenv
from scripts import binetflow_collection, raw_data, interim, preprocess


@click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
# def main(input_filepath, output_filepath):
def main():
    """
        Runs data collection scripts to create raw data.
        Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('1. making raw data set')
    logger.info('1.a downloading bi netflow')
    start_time = time.time()
    binetflow_collection.main()
    print(f'Time Elapsed: {time.time() - start_time}')

    logger.info('1.b create input.csv')
    start_time = time.time()
    raw_data.main()
    logger.info('raw data has been created')
    print(f'Time Elapsed: {time.time() - start_time}')

    logger.info('1.c create interim.csv')
    start_time = time.time()
    interim.main()
    logger.info('interim data has been created')
    print(f'Time Elapsed: {time.time() - start_time}')

    logger.info('1.d create preprocessed.csv')
    start_time = time.time()
    preprocess.main()
    logger.info('preprocessed data has been created')
    print(f'Time Elapsed: {time.time() - start_time}')

if __name__ == '__main__':
    LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)
    main()
