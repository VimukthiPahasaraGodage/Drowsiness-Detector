from flask import Flask, request, jsonify
import base64
import threading
import requests
import os
from video_trim_helper import trim_video
import time

app = Flask(__name__)

record_chunks = {}
main_output_file_path = "main_output.webm"
trim_output_file_path = "output.mp4"
previous_timestamp = 0
threads = []
sending_threads = []
trim_index_inspections = []

start = 0
end = 0
trim_index = 0


def current_milli_time():
    return round(time.time() * 1000)


def add_recording_to_dict(user_id, timestamp, record_key, record, reset=False):
    if user_id in record_chunks.keys():
        if reset:
            record_chunks[user_id] = [(timestamp, record_key, record)]
        else:
            record_chunks[user_id].append((timestamp, record_key, record))
    else:
        record_chunks[user_id] = [(timestamp, record_key, record)]
    sorted(record_chunks[user_id], key=lambda x: (x[0], x[1]))


def trim_and_send_video(index):
    global start
    global end
    global sending_threads
    global trim_index_inspections
    if end >= start + 60:
        trim_video(main_output_file_path, trim_output_file_path, start, start + 60)
        start += 60
    if os.path.exists(trim_output_file_path):
        with open(trim_output_file_path, "rb") as record_file:
            record_string = base64.b64encode(record_file.read())
            dict_to_send = {'UserId': 'Vimukthi', 'Time': str(current_milli_time()), 'Record': record_string.decode('utf-8')}
            res = requests.post('https://mha2r6r8a9.execute-api.us-east-1.amazonaws.com/postVideoData', json=dict_to_send)
            # check for the res variable for the success of the http request
            trim_index_inspections.append(index)
            print(res)
            print(trim_index_inspections)
    if len(sending_threads) > 0:
        sending_threads.pop(0)
        if len(sending_threads) > 0:
            sending_threads[0].start()


def create_small_videos_and_send(user_id, chunk):
    global start
    global end
    global sending_threads
    global trim_index
    bytes_of_chunk = base64.b64decode(chunk[2])
    if os.path.exists(main_output_file_path):
        binary_file = open(main_output_file_path, "ab")
        binary_file.write(bytes_of_chunk)
        binary_file.close()
        end += 60
    else:
        binary_file = open(main_output_file_path, "wb")
        binary_file.write(bytes_of_chunk)
        binary_file.close()
        start = 0
        end = 60
    sending_thread = threading.Thread(target=trim_and_send_video, args=(trim_index,))
    trim_index += 1
    sending_threads.append(sending_thread)
    if len(sending_threads) == 1:
        sending_threads[0].start()
    elif len(sending_threads) > 1:
        if not sending_threads[0].is_alive():
            sending_threads[0].start()


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Blob received successfully'})


# POST route to receive blob data
@app.route('/upload_blob', methods=['POST'])
def upload_blob():
    # Get the blob data from the request
    resp = request.get_json()
    user_id = resp['UserId']
    time = int(resp['Time'])
    record_key = int(resp['RecordKey'])
    record = (resp['Record']).split("base64,")[1]

    global record_chunks
    record_split = record.split("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    if len(record_split) > 1:
        record_tail = record_split[1]
        if record_tail == "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@":
            if os.path.exists(main_output_file_path):
                os.remove(main_output_file_path)
            add_recording_to_dict(user_id, time, record_key, record_split[0])
    elif len(record_split) == 1:
        add_recording_to_dict(user_id, time, record_key, record_split[0])

    if time > previous_timestamp:
        current_chunk = record_chunks[user_id].pop(0)
        thread = threading.Thread(target=create_small_videos_and_send, args=(user_id, current_chunk,))
        threads.append(thread)
        thread.start()

    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
