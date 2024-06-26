from flask import Flask, request, jsonify
import base64
import threading
import os
from ffmpeg_helper import trim_video

app = Flask(__name__)


record_chunks = {}
main_output_file_path = "main_output.webm"
previous_timestamp = 0
threads = []
sending_threads = []

start = 0
end = 0


def add_recording_to_dict(user_id, time, record_key, record, reset=False):
    if user_id in record_chunks.keys():
        if reset:
            record_chunks[user_id] = [(time, record_key, record)]
        else:
            record_chunks[user_id].append((time, record_key, record))
    else:
        record_chunks[user_id] = [(time, record_key, record)]
    sorted(record_chunks[user_id], key=lambda x: (x[0], x[1]))


def trim_and_send_video():
    global start
    global end
    if end >= start + 60:
        trim_video(main_output_file_path, "output.webm", start, start + 60)
        start -= 60
        end -= 60
    if os.path.exists("output.webm"):
        # send the recording to the API gateway
        # check for response if it is a success
        # then remove the output.webm
        # to send the webm file we need to first read the bytes from the file and add those bytes for the body of the POST request
    sending_threads.pop(0)
    if len(sending_threads) >= 1:
        sending_threads[0].start()


def create_small_videos_and_send(user_id, chunk):
    global start
    global end
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
    sending_thread = threading.Thread(target=trim_and_send_video())
    sending_threads.append(sending_thread)
    if len(sending_threads) == 1:
        sending_thread.start()
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
