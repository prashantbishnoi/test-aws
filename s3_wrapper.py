import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class S3Wrapper:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_image(self, image_id, image_data):
        try:
            s3_key = f"images/{image_id}.jpg"
            self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=image_data, ContentType='image/jpeg')
            return s3_key
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error uploading image to S3: {e}")
            raise

    def generate_presigned_url(self, image_id):
        try:
            s3_key = f"images/{image_id}.jpg"
            return self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket_name, 'Key': s3_key}, ExpiresIn=3600)
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    def delete_image(self, image_id):
        try:
            s3_key = f"images/{image_id}.jpg"
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error deleting image from S3: {e}")
            raise
