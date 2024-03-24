import boto3
import requests
import os
import json

class LambdaToEKSFileProcessor:
    def __init__(self, eks_processing_url, auth_token):
        self.s3_client = boto3.client('s3')
        self.eks_processing_url = eks_processing_url
        self.auth_token = auth_token

    def lambda_handler(self, event, context):
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            
            # Assuming direct file transfer is not feasible, pass S3 file reference to EKS
            file_reference = {
                "bucket_name": bucket_name,
                "object_key": object_key
            }
            
            # Trigger processing in EKS
            self.trigger_eks_processing(file_reference)

    def trigger_eks_processing(self, file_reference):
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.eks_processing_url, headers=headers, json=file_reference)
        
        if response.status_code == 200:
            print("Successfully triggered processing in EKS.")
        else:
            print(f"Failed to trigger processing in EKS. Status code: {response.status_code}, Response: {response.text}")

# Example usage:
# processor = LambdaToEKSFileProcessor('https://your-eks-processing-url', 'your_auth_token')
# processor.lambda_handler(event, context)
