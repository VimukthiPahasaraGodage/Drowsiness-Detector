import {post_data, get_data} from './api_helper.js';

let mediaStream;
let mediaRecorder;

function reset_local_storage(){
  chrome.storage.local.set({"record_1" : ""}).then(() => {
    console.log("Record 1 is cleared from the local storage");
  });

  chrome.storage.local.set({"record_2" : ""}).then(() => {
    console.log("Record 2 is cleared from the local storage");
  });
  
  chrome.storage.local.set({"max_record_key" : "0"}).then(() => {
    console.log("Max record key is set to 0 successfully");
  });

  chrome.storage.local.set({"stopped" : "0"}).then(() => {
    console.log("Stopped parameter is set to 0 successfully");
  });
}

async function code(command) {
  if (command == "stop" || command == "force_stop"){
    mediaRecorder.stop();
    mediaStream.getTracks().forEach(track => track.stop());
    
    chrome.storage.local.set({"record_1" : ""}).then(() => {
      console.log("Record 1 is cleared from the local storage");
    });

    chrome.storage.local.set({"record_2" : ""}).then(() => {
      console.log("Record 2 is cleared from the local storage");
    });
    
    chrome.storage.local.set({"max_record_key" : "0"}).then(() => {
      console.log("Max record key is set to 0 successfully");
    });

    if (command == "force_stop"){
      alert("Sleepiness Detector stopped due to and error!");
    }
  }else if (command == "start"){
    chrome.storage.local.set({"record_1" : ""}).then(() => {
      console.log("Record 1 is cleared from the local storage");
    });

    chrome.storage.local.set({"record_2" : ""}).then(() => {
      console.log("Record 2 is cleared from the local storage");
    });
    
    chrome.storage.local.set({"max_record_key" : "0"}).then(() => {
      console.log("Max record key is set to 0 successfully");
    });
  
    chrome.storage.local.set({"stopped" : "0"}).then(() => {
      console.log("Stopped parameter is set to 0 successfully");
    });

    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: true,
    });
  
    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: 'video/webm'
    });

    mediaRecorder.start(60000);

    let count = 0;
  
    mediaRecorder.ondataavailable = (event) => {
      let reader = new FileReader();
      reader.readAsDataURL(event.data);
      reader.onloadend = function () {
        let record = reader.result;
        chrome.storage.local.get("stopped", function (state) {
          let stopped = state['stopped'];
          if (stopped == "0"){
            chrome.storage.local.get("max_record_key", function (items) {
              let max_record_key = items['max_record_key'];
              max_record_key = parseInt(max_record_key, 10);
              if (max_record_key < 2){
                if (count == 0){
                  record += "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
                  count += 1
                }
                if (max_record_key == 0){
                  chrome.storage.local.set({"record_1" : record}).then(() => {
                    max_record_key = String(max_record_key);
                    chrome.storage.local.set({"max_record_key" : "1"}).then(() => {
                      //NOOP
                    });
                  });
                } else if (max_record_key == 1){
                  chrome.storage.local.set({"record_2" : record}).then(() => {
                    max_record_key = String(max_record_key);
                    chrome.storage.local.set({"max_record_key" : "2"}).then(() => {
                      //NOOP
                    });
                  });
                }      
              } else if (max_record_key >= 2){
                chrome.storage.local.set({"max_record_key" : "10000"}).then(() => {
                  //NOOP
                });
              }
            });
          } else if (stopped == "1"){
            chrome.storage.local.set({"record_1" : ""}).then(() => {
              console.log("Record 1 is cleared from the local storage");
            });

            chrome.storage.local.set({"record_2" : ""}).then(() => {
              console.log("Record 2 is cleared from the local storage");
            });
            
            chrome.storage.local.set({"max_record_key" : "0"}).then(() => {
              console.log("Max record key is set to 0 successfully");
            });
          }
        });
      }
    }
  }
}

const commands = {
  start: ["start"],
  stop: ["stop"],
  force_stop: ["force_stop"]
};

export async function executeScript(command) {
  if (!(command in commands)) return;
  const [tab] = await chrome.tabs.query({ active: true });
  const scriptInjection = {
    target: { tabId: tab.id },
    func: code,
    args: commands[command],
  }
  chrome.scripting.executeScript(scriptInjection);
}

export function alert_message_for_routine(routine){
  console.log("Alerting user about the routine " + routine);
  if (routine == "1"){
    chrome.notifications.create({
      title: "Sleepiness Detected",
      message: 'Get a sleep or take a break',
      type: "basic",
      iconUrl: "./assets/icon128.png"
    })
    playSound();
  }
}

chrome.runtime.onMessage.addListener(({command}) => {
  executeScript(command);
});

chrome.commands.onCommand.addListener((command) => {
  executeScript(command);
});

const create_alarm_for_sending_data = () => {
  chrome.alarms.create("Record_Sending_Alarm", {periodInMinutes: 1.0});
}

const create_alarm_for_retrieving_data = () => {
  chrome.alarms.create("Retrieve_Data_Alarm", {periodInMinutes: 1.0});
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name == "Record_Sending_Alarm"){
    console.log("Trying to send data...");
    chrome.storage.local.get("stopped", function (state) {
      let stopped = state['stopped'];
      if (stopped == "0"){
        chrome.storage.local.get("max_record_key", function (max_record_keys) {
          let max_record_key = parseInt(max_record_keys['max_record_key'], 10);
          if (max_record_key < 1) {
            console.log("No recordings have been produced to consume");
          } else if (max_record_key <= 2){
            console.log("Max record key: " + String(max_record_key));
            let timestamp = String(Date.now());
            for (let i = 1; i <= max_record_key; i++) {
              if (i == 1){
                chrome.storage.local.get("record_1", function (items_1) {
                  let record = items_1["record_1"];
                  post_data("Vimukthi", timestamp, "1", record);
                });
              } else if (i == 2){
                chrome.storage.local.get("record_2", function (items_2) {
                  let record = items_2["record_2"];
                  post_data("Vimukthi", timestamp, "2", record);
                });
              }
            }
            chrome.storage.local.set({"record_1" : ""}).then(() => {
              console.log("Record 1 is cleared from the local storage");
            });
          
            chrome.storage.local.set({"record_2" : ""}).then(() => {
              console.log("Record 2 is cleared from the local storage");
            });
            
            chrome.storage.local.set({"max_record_key" : "0"}).then(() => {
              console.log("Max record key is set to 0 successfully");
            });
          } else {
            // Something went wrong with consuming the recordings
            executeScript("force_stop");
            console.log("Recording production overflowed. Something is wrong with the consumer!")
          }
        });
      } else if (stopped == "1"){
        console.log("No recordings have been produced to consume");
      }
    });
  } else if (alarm.name == "Retrieve_Data_Alarm") {
    console.log("Trying to get data...");
    let timestamp = String(Date.now());
    get_data("Vimukthi", timestamp);
  }
})

async function playSound(source = 'audio.wav', volume = 1) {
  await createOffscreen();
  await chrome.runtime.sendMessage({ play: { source, volume } });
}

async function createOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;
  await chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['AUDIO_PLAYBACK'],
      justification: 'testing' // details for using the API
  });
}

// Execute starting logic
console.log("Drowsiness detector started!!!");

reset_local_storage();
create_alarm_for_sending_data();
create_alarm_for_retrieving_data();
