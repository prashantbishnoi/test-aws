import json
import uuid
import base64
import os
import logging
from botocore.exceptions import BotoCoreError, ClientError
from s3_wrapper import S3Wrapper
from dynamodb_wrapper import DynamoDBWrapper

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ImageHandler:
    def __init__(self):
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.table_name = os.getenv('TABLE_NAME')
        self.s3 = S3Wrapper(self.bucket_name)
        self.dynamodb = DynamoDBWrapper(self.table_name)

    def upload_image(self, event):
        try:
            body = json.loads(event['body'])
            image_data = base64.b64decode(body['image_data'])
            metadata = body.get('metadata', {})
            image_id = str(uuid.uuid4())

            self.s3.upload_image(image_id, image_data)
            self.dynamodb.save_metadata(image_id, metadata)

            logger.info(f"Image {image_id} uploaded successfully")
            return self._response(200, {'message': 'Image uploaded successfully', 'image_id': image_id})
        except (BotoCoreError, ClientError, KeyError, ValueError) as e:
            logger.error(f"Error uploading image: {e}")
            return self._response(500, {'error': str(e)})

    def list_images(self, event):
        try:
            filters = event.get('queryStringParameters', {}) or {}
            items = self.dynamodb.list_images(filters)
            logger.info("Listed images successfully")
            return self._response(200, {'images': items})
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error listing images: {e}")
            return self._response(500, {'error': str(e)})

    def view_image(self, event):
        try:
            image_id = event['pathParameters']['imageId']
            url = self.s3.generate_presigned_url(image_id)
            logger.info(f"Generated presigned URL for image {image_id}")
            return self._response(200, {'image_url': url})
        except (BotoCoreError, ClientError, KeyError) as e:
            logger.error(f"Error viewing image: {e}")
            return self._response(500, {'error': str(e)})

    def delete_image(self, event):
        try:
            image_id = event['pathParameters']['imageId']
            self.s3.delete_image(image_id)
            self.dynamodb.delete_metadata(image_id)
            logger.info(f"Image {image_id} deleted successfully")
            return self._response(200, {'message': 'Image deleted successfully'})
        except (BotoCoreError, ClientError, KeyError) as e:
            logger.error(f"Error deleting image: {e}")
            return self._response(500, {'error': str(e)})

    def _response(self, status_code, body):
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(body)
        }
