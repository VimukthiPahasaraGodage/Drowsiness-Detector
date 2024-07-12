import boto3
import time
import base64
import cv2
import dlib
import uuid

from scipy.spatial import distance
from boto3.dynamodb.conditions import Attr
from tqdm import tqdm

already_checked_timestamps = set()

dynamodb = boto3.resource('dynamodb',
                          region_name="us-east-1",
                          aws_access_key_id="AKIAZI2LCD2QHF4KI2NZ",
                          aws_secret_access_key="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")

video_table = dynamodb.Table('FacialVideoData')
inference_table = dynamodb.Table('DrowsinessInferences')

s3 = boto3.resource('s3',
                    aws_access_key_id="AKIAZI2LCD2QHF4KI2NZ",
                    aws_secret_access_key="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")


def get_timestamp():
    ts = round(time.time() * 1000)
    return ts


frame_padding = 250  # in milliseconds


def detect(video_file):
    awake = 0
    sleepy = 0

    face_detector = dlib.get_frontal_face_detector()

    dlib_facelandmark = dlib.shape_predictor(
        "C:\\shape_predictor_68_face_landmarks.dat")

    def Detect_Eye(eye):
        poi_A = distance.euclidean(eye[1], eye[5])
        poi_B = distance.euclidean(eye[2], eye[4])
        poi_C = distance.euclidean(eye[0], eye[3])
        aspect_ratio_Eye = (poi_A + poi_B) / (2 * poi_C)
        return aspect_ratio_Eye

    vidcap = cv2.VideoCapture(video_file)

    for frame_index in tqdm(range(300)):
        vidcap.set(cv2.CAP_PROP_POS_MSEC, frame_padding * frame_index)
        hasFrames, frame = vidcap.read()
        if not hasFrames or frame_index > 249:
            break
        else:
            frame_index += 1
        gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detector(gray_scale)

        for face in faces:
            face_landmarks = dlib_facelandmark(gray_scale, face)
            leftEye = []
            rightEye = []

            for n in range(42, 48):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                rightEye.append((x, y))
                next_point = n + 1
                if n == 47:
                    next_point = 42
                x2 = face_landmarks.part(next_point).x
                y2 = face_landmarks.part(next_point).y
                cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

            for n in range(36, 42):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                leftEye.append((x, y))
                next_point = n + 1
                if n == 41:
                    next_point = 36
                x2 = face_landmarks.part(next_point).x
                y2 = face_landmarks.part(next_point).y
                cv2.line(frame, (x, y), (x2, y2), (255, 255, 0), 1)

            right_Eye = Detect_Eye(rightEye)
            left_Eye = Detect_Eye(leftEye)
            Eye_Rat = (left_Eye + right_Eye) / 2

            Eye_Rat = round(Eye_Rat, 2)

            if Eye_Rat < 0.25:
                cv2.putText(frame, "DROWSINESS DETECTED", (50, 100),
                            cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 210), 3)
                cv2.putText(frame, "Alert!!!! WAKE UP DUDE", (50, 450),
                            cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 212), 3)
                # print("DROWSINESS DETECTED")
                sleepy += 1
            else:
                # print("STILL AWAKE")
                awake += 1
    print(str(awake) + " awakeness and " + str(sleepy) + " sleepiness detected")
    return sleepy > awake


s3.Bucket("facialvideorecordings").download_file("shape_predictor_68_face_landmarks.dat",
                                                 'shape_predictor_68_face_landmarks.dat')

while True:
    scan_timestamp = get_timestamp() - (60000 * 4)
    response = video_table.scan(
        FilterExpression=Attr('UserId').eq('Vimukthi') & Attr('Time').gt(str(scan_timestamp)) & Attr(
            'StatusOfRecord').eq('Unprocessed')
    )

    items = response['Items']
    if len(items) < 1:
        print("Not items to detect\n")
        time.sleep(30)
        continue

    timestamp = 1000000000000000000000000000000
    record_id_of_database_item = None
    user_id = None
    file_path = None
    status = None
    for record in items:
        record_time = int(record['Time'])
        if record_time < timestamp:
            timestamp = record_time
            record_id_of_database_item = record['RecordId']
            user_id = record['UserId']
            file_path = record['FilePath']
            status = record['StatusOfRecord']
    print("Processing the recording for the timestamp: " + str(timestamp) + " for sleepiness")

    video_filename = file_path + ".mp4"

    s3.Bucket("facialvideorecordings").download_file(file_path, file_path)
    with open(file_path, 'r') as file:
        base64string = file.read()
        file = open(video_filename, "wb")
        file.write(base64.b64decode(base64string))
        file.close()

    # frame_index, frames = get_frames_from_video(video_filename, timestamp)
    is_sleepy = detect(video_filename)
    # already_checked_timestamps.add(timestamp)

    record_id = uuid.uuid4()
    inference = "Awake"
    if is_sleepy:
        inference = "Sleepy"

    inference_table.put_item(
        Item={
            'RecordId': str(record_id),
            'UserId': 'Vimukthi',
            'Time': str(timestamp),
            'Inference': inference
        })

    delete_response = video_table.delete_item(
        Key={
            'RecordId': str(record_id_of_database_item),
            'UserId': 'Vimukthi'
        }
    )

    update_response = video_table.put_item(
        Item={
            "RecordId": str(record_id_of_database_item),
            "UserId": user_id,
            "Time": str(timestamp),
            "FilePath": file_path,
            "StatusOfRecord": "Processed"})

    print("Therefore, the inference for timestamp: " + str(timestamp) + " is that the user is " + inference + "\n")
