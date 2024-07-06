import json
import boto3
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    print(event)
    user_id = event['headers']['userid']
    time = event['headers']['time']

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table('DrowsinessInferences')
    response = table.scan(
        FilterExpression=Attr('UserId').eq('Vimukthi') & Attr('Time').lt(str(time))
    )

    message = ""

    items = response['Items']

    if len(items) >= 2:
        awake = 0
        sleepy = 0
        timestamps = []
        timestamp_inference = {}
        for item in items:
            timestamp = item['Time']
            timestamps.append(int(item['Time']))
            timestamp_inference[timestamp] = item['Inference']
        timestamps = sorted(timestamps)

        for i in range(1, 3):
            timestamp = timestamps[-1 * i]
            infer = timestamp_inference[str(timestamp)]
            if infer == "Awake":
                awake += 1
            elif infer == "Sleepy":
                sleepy += 1

        routine_name = "0"
        if sleepy > awake:
            routine_name = "1"

        message = "Routine_" + routine_name
    else:
        message = ""

    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }
