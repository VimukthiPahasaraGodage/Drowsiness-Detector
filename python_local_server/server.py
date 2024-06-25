from flask import Flask, request, jsonify
import base64

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Blob received successfully'})

# POST route to receive blob data
@app.route('/upload_blob', methods=['POST'])
def upload_blob():
    # Get the blob data from the request
    resp = request.get_json()
    user_id = resp['UserId']
    time = resp['Time']
    record = resp['Record']

    record = record.split("base64,")[1]
    bytes = base64.b64decode(record)

    binary_file = open("my_file.webm", "wb")
    binary_file.write(bytes)
    binary_file.close()


    # base64string = blob.split("base64,")[1]

    
    # Convert blob (which is already bytes) into a byte array (if needed)
    # byte_array = bytearray(blob)
    
    # Optionally, process the byte array further if needed
    
    # Return a response (optional)
    return jsonify({'message': 'jghjfdjh'})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
