import boto3
import os
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd
from PIL import Image

s3_client = boto3.client('s3')
upload_bucket_name = 'your-target-bucket-name'

def process_files(directory):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            data_type = identify_data_type(filename)
            if data_type in ['xml', 'csv']:
                content = process_text_file(full_path, data_type)
            elif data_type in ['gif', 'jpeg']:
                content = process_image_file(full_path, filename)
            else:
                continue  # Skip unsupported file types

            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            target_filename = f"{filename}-{timestamp}.json"
            s3_client.put_object(Bucket=upload_bucket_name, Key=target_filename, Body=json.dumps(content, indent=4))
            print(f"Uploaded {target_filename} to S3 bucket {upload_bucket_name}.")

def identify_data_type(filename):
    extension = filename.split('.')[-1].lower()
    return extension

def process_text_file(path, data_type):
    if data_type == 'xml':
        return process_xml_file(path)
    elif data_type == 'csv':
        return process_csv_file(path)

def process_xml_file(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return {root.tag: {child.tag: child.text for child in root}}

def process_csv_file(path):
    df = pd.read_csv(path)
    return df.to_dict(orient='records')

def process_image_file(path, filename):
    with Image.open(path) as img:
        metadata = {
            "filename": filename,
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
        }
    return metadata

# Example usage: process_files('/path/to/your/directory')
