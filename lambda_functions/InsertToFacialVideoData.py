import json
import uuid
import boto3


def lambda_handler(event, context):
    print(event)

    # Get data from the POST request body
    request_body = json.loads(event["body"])
    user_id = request_body["UserId"]
    time = request_body["Time"]
    # record_key = request_body["RecordKey"]
    record = request_body["Record"]
    record_id = str(uuid.uuid4())

    bucket_name = "facialvideorecordings"
    s3_file_path = user_id + "_" + time

    s3 = boto3.resource('s3')

    s3.Object(bucket_name, s3_file_path).put(Body=record)

    # Prepare the DynamoDB client
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("FacialVideoData")
    table.put_item(Item={"RecordId": record_id, "UserId": user_id, "Time": time, "FilePath": s3_file_path,
                         "StatusOfRecord": "Unprocessed"})

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
