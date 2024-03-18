import boto3

class S3DataClassifier:
    def __init__(self):
        self.s3_client = boto3.client('s3')

    def lambda_handler(self, event, context):
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            data_type = self.identify_data_type(object_key)
            
            # Tag the S3 object
            self.tag_s3_object(bucket_name, object_key, data_type)

    def identify_data_type(self, file_key):
        structured_extensions = ['csv', 'txt', 'xml']
        extension = file_key.split('.')[-1].lower()
        return 'structured' if extension in structured_extensions else 'unstructured'

    def tag_s3_object(self, bucket, key, data_type):
        try:
            self.s3_client.put_object_tagging(
                Bucket=bucket,
                Key=key,
                Tagging={
                    'TagSet': [
                        {
                            'Key': 'data-type',
                            'Value': data_type
                        },
                    ]
                }
            )
            print(f"Successfully tagged {key} as {data_type}")
        except Exception as e:
            print(f"Failed to tag {key}. Error: {e}")

# Example usage:
# handler = S3DataClassifier()
# handler.lambda_handler(event, context)
