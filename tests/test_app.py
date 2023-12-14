import pytest
import os
import boto3
from moto import mock_s3

BUCKET = "test-bucket"

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
