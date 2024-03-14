import boto3
import base64
from datetime import datetime

class MSKToS3Handler:
    def __init__(self, s3_bucket):
        self.s3_client = boto3.client('s3')
        self.s3_bucket = s3_bucket

    def lambda_handler(self, event, context):
        for record in event['records']:
            topic_arn = record['eventSourceARN']
            topic_name = self.extract_topic_name(topic_arn)
            file_content = base64.b64decode(record['value'])  # Assuming the payload is base64 encoded
            file_name = self.generate_file_name(topic_name)
            
            self.upload_to_s3(file_name, file_content, topic_name)

    def extract_topic_name(self, topic_arn):
        # Extract the topic name from the ARN
        return topic_arn.split(':')[-1]

    def generate_file_name(self, topic_name):
        # Generate a unique file name using the topic name and current timestamp
        # This is a placeholder implementation. Adapt as necessary.
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        return f"{topic_name}/{timestamp}.bin"

    def upload_to_s3(self, file_name, file_content, topic_name):
        try:
            self.s3_client.put_object(Bucket=self.s3_bucket, Key=file_name, Body=file_content)
            print(f"Successfully uploaded {file_name} to S3 bucket {self.s3_bucket}.")
        except Exception as e:
            print(f"Failed to upload {file_name} to S3. Error: {e}")

# Example usage:
# handler = MSKToS3Handler('your-s3-bucket-name')
# handler.lambda_handler(event, context)
