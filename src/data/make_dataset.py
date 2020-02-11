#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    This is the main file to making the dataset.q
    This will download data, create the raw data and preprocces it.
'''
import logging
import click
# from pathlib import Path
# from dotenv import find_dotenv, load_dotenv
from scripts import binetflow_collection
from scripts import raw_data


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
    binetflow_collection.main()
    logger.info('1.b create input.csv')
    raw_data.main()
    logger.info('raw data has been created')
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)

    # # not used in this stub but often useful for finding various files
    # project_dir = Path(__file__).resolve().parents[2]

    # # find .env automagically by walking up directories until it's found, then
    # # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
