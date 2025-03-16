import json
import boto3
import uuid
import base64
import os
import logging
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ImageHandler:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.table_name = os.getenv('TABLE_NAME')
        self.table = self.dynamodb.Table(self.table_name)

    def upload_image(self, event):
        try:
            body = json.loads(event['body'])
            image_data = base64.b64decode(body['image_data'])
            metadata = body.get('metadata', {})
            image_id = str(uuid.uuid4())
            s3_key = f"images/{image_id}.jpg"

            self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=image_data, ContentType='image/jpeg')
            self.table.put_item(Item={'imageId': image_id, 'metadata': metadata})

            logger.info(f"Image {image_id} uploaded successfully")
            return self._response(200, {'message': 'Image uploaded successfully', 'image_id': image_id})
        except (BotoCoreError, ClientError, KeyError, ValueError) as e:
            logger.error(f"Error uploading image: {e}")
            return self._response(500, {'error': str(e)})

    def list_images(self, event):
        try:
            filters = event.get('queryStringParameters', {}) or {}
            response = self.table.scan()
            items = response.get('Items', [])

            if filters:
                items = [item for item in items if all(item['metadata'].get(k) == v for k, v in filters.items())]

            logger.info("Listed images successfully")
            return self._response(200, {'images': items})
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error listing images: {e}")
            return self._response(500, {'error': str(e)})

    def view_image(self, event):
        try:
            image_id = event['pathParameters']['imageId']
            s3_key = f"images/{image_id}.jpg"
            url = self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket_name, 'Key': s3_key},
                                                 ExpiresIn=3600)

            logger.info(f"Generated presigned URL for image {image_id}")
            return self._response(200, {'image_url': url})
        except (BotoCoreError, ClientError, KeyError) as e:
            logger.error(f"Error viewing image: {e}")
            return self._response(500, {'error': str(e)})

    def delete_image(self, event):
        try:
            image_id = event['pathParameters']['imageId']
            s3_key = f"images/{image_id}.jpg"

            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            self.table.delete_item(Key={'imageId': image_id})

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
