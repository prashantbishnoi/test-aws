# API Documentation and Usage Instructions

## Overview
This API provides functionality for uploading, listing, viewing, and deleting images. It is built using AWS API Gateway, Lambda, S3, and DynamoDB. The API supports JSON-based requests and responses.

## Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/
```
(The exact URL can be found in the CloudFormation outputs under `ApiGatewayEndpoint`.)

## Endpoints

### 1. Upload Image
#### Endpoint
```
POST /upload
```
#### Request
**Headers:**
```
Content-Type: application/json
```
**Body:**
```json
{
  "image_data": "<base64_encoded_image>",
  "metadata": {
    "tag": "example",
    "description": "Sample image upload"
  }
}
```
#### Response
**Success (200 OK):**
```json
{
  "message": "Image uploaded successfully",
  "image_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 2. List Images
#### Endpoint
```
GET /images
```
#### Query Parameters (Optional Filters)
```
tag=example&description=Sample
```
#### Response
**Success (200 OK):**
```json
{
  "images": [
    {
      "imageId": "123e4567-e89b-12d3-a456-426614174000",
      "metadata": {
        "tag": "example",
        "description": "Sample image upload"
      }
    }
  ]
}
```

### 3. View Image
#### Endpoint
```
GET /image/{imageId}
```
#### Response
**Success (200 OK):**
```json
{
  "image_url": "https://s3.amazonaws.com/bucket-name/images/123e4567-e89b-12d3-a456-426614174000.jpg"
}
```

### 4. Delete Image
#### Endpoint
```
DELETE /image/{imageId}
```
#### Response
**Success (200 OK):**
```json
{
  "message": "Image deleted successfully"
}
```

## Error Handling
All endpoints return standard HTTP status codes:
- `400 Bad Request`: Invalid input.
- `404 Not Found`: Image not found.
- `500 Internal Server Error`: Unexpected server error.

## Authentication
Currently, the API does not enforce authentication, but IAM-based authorization can be integrated for secure access.

## Deployment & Usage
- Deploy the CloudFormation template to set up resources.
- Upload the Lambda function code zip to the bucket mentioned in the cloudformation parameter:
- Deploy the CloudFormation stack to apply the changes.
- Invoke the API using tools like Postman or `curl`.

For further details, refer to the CloudFormation template output values to retrieve actual resource names and endpoints.

