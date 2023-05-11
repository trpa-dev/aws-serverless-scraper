#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "trpa-dev"
__version__ = "0.1.0"
__license__ = "MIT"

from datetime import datetime
import json
import logging
import os

from bs4 import BeautifulSoup
from fastparquet import write
import boto3
import pandas as pd
import requests


def get_data_from_page(soup: BeautifulSoup) -> pd.DataFrame:
    """ Parses BeautifulSoup into a DataFrame """
    card_tag = 'li'
    card_class = 'col-xs-6 col-sm-4 col-md-3 col-lg-3'
    book_cards = soup.find_all(card_tag, class_=card_class)
    book_title_list = []
    book_price_list = []
    book_stock_status_list = []

    for item in book_cards:
        book_title_list.append(item.find('h3').find('a')['title'])
        book_price_list.append(
            item.find('p', class_='price_color').text[1:]
        )
        book_stock_status_list.append(
            item.find('p', class_='instock availability').text.strip()
        )

    chunk_df = pd.DataFrame(
        {
            'book_title': book_title_list,
            'book_record_date': str(datetime.today().date()),
            'book_price': book_price_list,
            'book_stock_status': book_stock_status_list
        }
    )

    return chunk_df


def save_df_to_parquet(input_df: pd.DataFrame, file_name: str) -> str:
    """ Save DataFrame as a Parquet file format """
    lambda_scratch_dir = '/tmp/'
    temp_file_path = file_name
    if os.path.isdir(lambda_scratch_dir):
        temp_file_path = lambda_scratch_dir + file_name

    write(temp_file_path, input_df, compression='GZIP')

    return temp_file_path

def put_parquet_to_s3(file_path: str):
    """ Push Parquet file to S3 """
    bucket_name = 'my-lambda-layer-test'
    s3_path = 'scraped/' + file_path[1:]
    s3_api = boto3.resource("s3")
    s3_api.meta.client.upload_file(file_path, bucket_name, s3_path)


def handler(event, context):
    """ Main entry point of Lambda"""
    logging.basicConfig(level=logging.INFO)
    logging.info("Program start")
    scraping_url = 'http://books.toscrape.com/catalogue/page-1.html'
    navigation_url = 'http://books.toscrape.com/catalogue/'
    response = requests.get(scraping_url)
    logging.info(scraping_url)
    logging.info(response)

    soup = BeautifulSoup(response.text, features='html.parser')
    main_df = get_data_from_page(soup)

    next_page_url = soup.find('li', class_='next').find('a')['href']
    while next_page_url:
        next_page_url = navigation_url + next_page_url
        logging.info(next_page_url)
        response = requests.get(next_page_url)
        soup = BeautifulSoup(response.text, features='html.parser')
        main_df = pd.concat([main_df, get_data_from_page(soup)], ignore_index=True)
        try:
            next_page_url = soup.find('li', class_='next').find('a')['href']
        except AttributeError:
            logging.info("No more pages found")
            break

    logging.info('Rows scraped: %s', len(main_df.index))

    file_name = str(datetime.today().date()).replace('-', '') + '_books.parq'

    temp_file_path = save_df_to_parquet(main_df, file_name)

    put_parquet_to_s3(temp_file_path)

    return {
        'statusCode': 200,
        'body': json.dumps('Ran successfully!')
    }

if __name__ == "__main__":
    handler(None, None)
