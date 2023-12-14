import json
import pendulum
from airflow.decorators import dag, task
from common import load_from_s3, load_mapping_columns, deduplicate, dataframe_to_s3, write_to_sqlite
import pandas as pd

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def brightwheel_etl_nevada():
    """
    ### BrightWheel ETL take-home exercise
    This DAG is the submission to the take-home exercise, by Andy Sprague.
    """

    @task()
    def extract_nevada():
        """
        #### Extract task
        Read in the file(s) from s3.
        """
        s3_path = 'data/Data_Eng_Exercise_Files/07-07-2023 Nevada Dept of Public _ Behavioral Health.csv'  # TODO parameterize?
        bucket = 'brightwheel-andy' # TODO put in config
        df = load_from_s3(bucket=bucket, s3_path=s3_path)

        print(f'Loaded data with {len(df)} lines')

        path = dataframe_to_s3(df, bucket, 'staging/nevada/07-07-2023/in.csv')
        print(f'saved to {path}')
        return path


    @task()
    def transform_nevada(s3_path: str):
        """
        #### Transform task
        Takes the extracted dataframe and transform it to a common schema
        """
        bucket = 'brightwheel-andy' # TODO put in config
        df = load_from_s3(bucket=bucket, s3_path=s3_path)
        
        mapping_dict = load_mapping_columns('nevada')
        df = df[mapping_dict.keys()]
        df = df.rename(columns=mapping_dict)
        print(f'Transformed data')

        
        path = dataframe_to_s3(df, bucket, 'transformed/nevada/07-07-2023/in.csv')
        print(f'saved to {path}')

        return path

    @task()
    def load_nevada(s3_path: str):
        """
        #### Load task
        Take the dataframe from the transform task and load it to the target DB.
        """
        bucket = 'brightwheel-andy' # TODO put in config
        df = load_from_s3(bucket=bucket, s3_path=s3_path)
        write_to_sqlite(df)        
        return True

    
    # Define 'task flow'
    df_raw_path = extract_nevada()
    df_transform_path = transform_nevada(df_raw_path)
    load_is_complete = load_nevada(df_transform_path)
    deduplicate(load_is_complete)

brightwheel_etl_nevada()
