import json
import pendulum
import json
import gzip
import boto3
import os
import chardet
import pandas as pd
import sqlite3
from typing import Any
from io import StringIO, BytesIO
from airflow.decorators import task

@task()
def deduplicate(load_is_complete):
    """
    #### Deduplication
    Creates downstream tables or materialized views in the data warehouse without dupes (based on pk/sk).

    This is common for all files and triggered by each new upload, as we want to de-dupe across sources.
    """
    # TODO
    print('deduplication started')
    return 'ok'


def load_from_s3(bucket: str, s3_path: str) -> pd.DataFrame:
    """Load a csv file in s3 to a pandas dataframe."""
    # TODO should be able to handle .gz files with pd.read_csv option 'compression'
    s3 = boto3.resource('s3')
    response = s3.Object(bucket_name=bucket, key=s3_path).get()
    contents = response.get("Body").read()
    enc = chardet.detect(contents)
    contents = contents.decode(enc['encoding'])
    df = pd.read_csv(StringIO(contents))
    return df


def dataframe_to_s3(df, bucket, s3_path):
        out_buffer = BytesIO()
        df.to_csv(out_buffer, index=False)
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=s3_path, Body=out_buffer.getvalue())
        return s3_path


def load_mapping_columns(state: str):
    supported_states = ['nevada'] # , 'Oklahoma', 'Texas']
    state = state.lower()
    if state not in supported_states:
        raise ValueError(f'State {state} not yet supported, must be one of [{", ".join(supported_states)}]')

    file_path = os.path.join(os.path.dirname(__file__), 'column_mapping.csv')
    df = pd.read_csv(file_path)
    df = df[['target_column', state]]
    df = df.dropna(subset=state)
    mapping_dict = df.set_index(state)['target_column'].to_dict()
    return mapping_dict


def write_to_sqlite(df: pd.DataFrame):
    with sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', '..', 'airflow.db')) as conn:
        try:
            c = conn.cursor()
            df.to_sql('leads', conn, if_exists='replace', index=False)
            conn.commit()
        except:
            conn.rollback()
            raise
