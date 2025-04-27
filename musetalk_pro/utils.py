import requests
import boto3
import os
from dotenv import load_dotenv

def download_file(file_url, save_path):
    response = requests.get(file_url)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(response.content)

def upload_to_s3(local_file_path, bucket_name, s3_key, aws_access_key_id, aws_secret_access_key, region_name="us-east-1"):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name=region_name)
    s3.upload_file(local_file_path, bucket_name, s3_key)
    print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_key}")

def log_result(result):
    print("MuseTalk API Response:")
    print(result)

    video_info = result['video']
    file_url = video_info['url']
    file_name = video_info['file_name']

    print("Downloading the result video...")
    download_file(file_url, file_name)
    print(f"Downloaded {file_name} successfully.")

    print("Uploading to S3...")
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_key = f"outputVids/{file_name}"

    upload_to_s3(f"/Users/vivivis/musetalk_pro/outputxxx_My+Movie_9.mp4", bucket_name, s3_key, aws_access_key_id, aws_secret_access_key)
    print("Upload to S3 finished successfully!")