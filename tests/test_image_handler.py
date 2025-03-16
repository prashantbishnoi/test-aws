import unittest
from unittest.mock import patch
import json
import base64
from image_handler import ImageHandler
from imager import lambda_handler


class TestImageHandler(unittest.TestCase):

    @patch("boto3.client")
    @patch("boto3.resource")
    def setUp(self, mock_dynamodb, mock_s3):
        self.mock_s3 = mock_s3.return_value
        self.mock_dynamodb = mock_dynamodb.return_value
        self.mock_table = self.mock_dynamodb.Table.return_value
        self.image_handler = ImageHandler()

    def test_upload_image_success(self):
        event = {
            "body": json.dumps({
                "image_data": base64.b64encode(b"test_image").decode("utf-8"),
                "metadata": {"tag": "test", "description": "test image"}
            })
        }
        response = self.image_handler.upload_image(event)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("image_id", json.loads(response["body"]))

    def test_list_images_success(self):
        self.mock_table.scan.return_value = {"Items": [{"imageId": "123", "metadata": {}}]}
        event = {}
        response = self.image_handler.list_images(event)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("images", json.loads(response["body"]))

    def test_view_image_success(self):
        self.mock_s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/test.jpg"
        event = {"pathParameters": {"imageId": "123"}}
        response = self.image_handler.view_image(event)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("image_url", json.loads(response["body"]))

    def test_delete_image_success(self):
        event = {"pathParameters": {"imageId": "123"}}
        response = self.image_handler.delete_image(event)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("message", json.loads(response["body"]))


class TestLambdaHandler(unittest.TestCase):

    @patch("imager.ImageHandler")
    def test_lambda_handler_upload(self, MockHandler):
        mock_instance = MockHandler.return_value
        mock_instance.upload_image.return_value = {"statusCode": 200, "body": json.dumps({"message": "Success"})}

        event = {"httpMethod": "POST", "resource": "/upload", "body": json.dumps({"image_data": "test"})}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)

    @patch("imager.ImageHandler")
    def test_lambda_handler_invalid(self, MockHandler):
        event = {"httpMethod": "POST", "resource": "/invalid"}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))


if __name__ == "__main__":
    unittest.main()
