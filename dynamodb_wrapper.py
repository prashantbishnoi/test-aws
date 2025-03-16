import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DynamoDBWrapper:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save_metadata(self, image_id, metadata):
        try:
            self.table.put_item(Item={'imageId': image_id, 'metadata': metadata})
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error saving metadata to DynamoDB: {e}")
            raise

    def list_images(self, filters):
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            if filters:
                items = [item for item in items if all(item['metadata'].get(k) == v for k, v in filters.items())]
            return items
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error retrieving images from DynamoDB: {e}")
            raise

    def delete_metadata(self, image_id):
        try:
            self.table.delete_item(Key={'imageId': image_id})
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error deleting metadata from DynamoDB: {e}")
            raise
