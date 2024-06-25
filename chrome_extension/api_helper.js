import {alert_message_for_routine, executeScript} from './background.js';

export function post_data(user_id, timestamp, record_key, record){
  fetch("http://127.0.0.1:5000/upload_blob", {
    method: "POST",
    body: JSON.stringify({
      UserId: user_id,
      Time: timestamp,
      RecordKey: record_key,
      Record: record
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log("Sending record with RecordKey: " + record_key + " is " + data['result']);
  })
  .catch(error => {
    console.log("Error while sending the record with RecordKey: " + record_key + ", Error: " + error);
    chrome.storage.local.set({"stopped" : "1"}).then(() => {
      console.log("Stopped parameter is set to 1 successfully");
    });
    executeScript("force_stop");
  });
}

function handle_routine(routine){
  console.log("Taking actions for routine " + String(routine));
  alert_message_for_routine(String(routine));
}

export function get_data(user_id, timestamp){
  fetch("https://mha2r6r8a9.execute-api.us-east-1.amazonaws.com/getInference", {
    method: 'GET',
    headers: {
      'UserId': user_id,
      'Time': timestamp
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data == ""){
      console.log("Response : No data");
    }else{
      console.log("Response : " + data);
      let routine = parseInt(data.split("_")[1], 10);
      handle_routine(routine);
    }
  })
  .catch(error => {
    console.log("Error : " + error);
  });
}