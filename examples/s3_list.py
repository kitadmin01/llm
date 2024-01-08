import boto3
from botocore.exceptions import NoCredentialsError

s3_client = boto3.client('s3')
bucket_name = 'jumpstart-cache-prod-us-east-2'
prefix = 'training-datasets'

response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
for item in response.get('Contents', []):
    print(item['Key'])

import boto3


def download_file_from_s3(bucket_name, s3_file_path, local_file_path):
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, s3_file_path, local_file_path)
        print(f"File downloaded successfully: {local_file_path}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error downloading file: {e}")

s3_file_path = 'training-datasets/Amazon_SageMaker_FAQs/Amazon_SageMaker_FAQs.csv'  # Path of the file in the bucket
local_file_path = 'Amazon_SageMaker_FAQs.csv'  # Local path where you want to save the file

download_file_from_s3(bucket_name, s3_file_path, local_file_path)
