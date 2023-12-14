import pytest
import os
import boto3
from moto import mock_s3
import pandas as pd
import sqlite3

BUCKET = "test-bucket"

def __load_fixture_as_df(file_name):
    """Load a test csv from fixture folder"""
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", file_name)
    df = pd.read_csv(file_path)
    return df

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def s3(aws_credentials):
    with mock_s3():
        conn = boto3.resource("s3", region_name="us-east-1")
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        conn.create_bucket(Bucket=BUCKET)

        # upload our test files to the virtual s3 bucket
        fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures'))
        for f in os.listdir(fixtures_dir):
            conn.Bucket(BUCKET).upload_file(os.path.join(fixtures_dir, f), f"data/Data_Eng_Exercise_Files/{f}")

        yield conn


def test_placeholder():
    assert 1 == 1


def test_list_s3_files(s3):
    s3 = boto3.resource("s3", region_name="us-east-1")
    s3_bucket = s3.Bucket(name=BUCKET)

    # Get the iterator from the S3 objects collection
    files = [f.key for f in s3_bucket.objects.filter(Prefix='data/')]
    # files = s3.list_objects_v2(Bucket='brightwheel-andy', Prefix="data/")

    assert files is not None
    assert len(files) == 3
    

def test_load_file_from_s3(s3):
    from src.dags.common import load_from_s3
    df = load_from_s3(BUCKET, 'data/Data_Eng_Exercise_Files/07-07-2023 Nevada Dept of Public _ Behavioral Health.csv')
    assert df is not None
    assert len(df) == 5


def test_load_mapping():
    from src.dags.common import _load_mapping_columns
    mapping_dict = _load_mapping_columns('nevada')
    assert mapping_dict is not None
    assert 'Name' in mapping_dict
    assert mapping_dict['Name'] == 'company'


def test_transform():
    # Assemble
    from src.dags.common import transform
    df = __load_fixture_as_df("07-07-2023 Nevada Dept of Public _ Behavioral Health.csv")

    #Act
    df = transform(df, 'nevada')

    #Used to generate input for next test
    # file_path = os.path.join(os.path.dirname(__file__), "fixtures", 'tranformed-nevada.csv')
    # df.to_csv(file_path, index=False)

    #Assert
    assert df is not None
    assert 'company' in df.columns
    assert df.iloc[0].company == 'SUNSHINE ACADEMY PRE-SCHOOL'


def test_write_to_target_db():
    from src.dags.common import write_to_sqlite
    df = __load_fixture_as_df("tranformed-nevada.csv")
    write_to_sqlite(df)

    with sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'airflow.db')) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM leads WHERE company = 'SUNSHINE ACADEMY PRE-SCHOOL'")
        rows = cur.fetchall()
    assert rows is not None
    assert len(rows) == 1
    assert rows[0][4] == 'CLARK' # county

    #writing again should replace not add
    df.iloc[0].county = 'NOT CLARK'
    write_to_sqlite(df)
    with sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'airflow.db')) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM leads WHERE company = 'SUNSHINE ACADEMY PRE-SCHOOL'")
        rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][4] == 'NOT CLARK' # county
