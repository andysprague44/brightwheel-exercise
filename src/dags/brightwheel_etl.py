import json
import pendulum
from airflow.decorators import dag, task
from common import load_from_s3


@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def brightwheel_etl():
    """
    ### BrightWheel ETL take-home exercise
    This DAG is the submission to the take-home exercise, by Andy Sprague.
    It loads from s3, does the transforms, and uploads to redshift
    """

    @task()
    def extract():
        """
        #### Extract task
        Read in the file(s) from s3.
        """
        s3_path = 'data/Data_Eng_Exercise_Files/07-07-2023 Nevada Dept of Public _ Behavioral Health.csv'  # TODO parameterize
        bucket = 'brightwheel-andy' # TODO put in config
        df = load_from_s3(bucket=bucket, s3_path=s3_path)
        
        print(f'Loaded data with {len(df)} lines')
        return df


    @task(multiple_outputs=True)
    def transform(df: pd.DataFrame):
        """
        #### Transform task
        Takes the extracted datafarame and transform it to a common schema
        """
        total_order_value = 0

        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}

    @task()
    def load(df: pd.DataFrame):
        """
        #### Load task
        Take the dataframe from the transform task and load it to the target DB.
        """

        print(f"Total order value is: {total_order_value:.2f}")

    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])


tutorial_taskflow_api()
