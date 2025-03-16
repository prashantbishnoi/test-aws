import json
import logging
from image_handler import ImageHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    handler = ImageHandler()
    http_method = event['httpMethod']
    resource = event['resource']

    if http_method == 'POST' and resource == '/upload':
        return handler.upload_image(event)
    elif http_method == 'GET' and resource == '/images':
        return handler.list_images(event)
    elif http_method == 'GET' and resource.startswith('/image/'):
        return handler.view_image(event)
    elif http_method == 'DELETE' and resource.startswith('/image/'):
        return handler.delete_image(event)
    else:
        logger.error("Invalid request received")
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid request'})}
