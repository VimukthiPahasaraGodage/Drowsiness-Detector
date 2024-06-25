import {post_data, get_data} from './api_helper.js';

function code(command) {
  // let chunks = []
  navigator.mediaDevices.getUserMedia({
    video: true,
  }).then(mediaStream => {
    // Use MediaStream Recording API
    const mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: 'video/webm'
  });
    // Make the mediaStream global 
    window.mediaStream = mediaStream; 
    // Make the mediaRecorder global 
    window.mediaRecorder = mediaRecorder;
    // fires every one second and passes an BlobEvent
    window.mediaRecorder.ondataavailable = event => {
      let reader = new FileReader();
      reader.readAsDataURL(event.data);
      reader.onloadend = function () {
        let record = reader.result;
        chrome.storage.local.set({"record": record}).then(() => {
          //NOOP
        });
      }
      // chunks.push(event.data)

      // var tempLink = document.createElement("a");
      // let timestamp = String(Date.now());
      // //var textBlob = new Blob([base64String], {type: 'text/plain'});
      // tempLink.setAttribute('href', URL.createObjectURL(event.data));
      // tempLink.setAttribute('download', timestamp + ".webm");
      // tempLink.click();

      // var tempLink_r = document.createElement("a");
      // var textBlob = new Blob(chunks, {type: 'video/webm'});
      // tempLink_r.setAttribute('href', URL.createObjectURL(textBlob));
      // tempLink_r.setAttribute('download', timestamp + "_full.webm");
      // tempLink_r.click();
      //window.mediaRecorder.stop();

      // let reader = new FileReader();
      // reader.readAsDataURL(event.data);
      // reader.onloadend = function () {
      //   let base64String = reader.result;
      //   var tempLink = document.createElement("a");
      //   let timestamp = String(Date.now());
      //   var textBlob = new Blob([base64String], {type: 'text/plain'});
      //   tempLink.setAttribute('href', URL.createObjectURL(textBlob));
      //   tempLink.setAttribute('download', timestamp + ".txt");
      //   tempLink.click();
        // chrome.storage.local.get("record", function (items) {
        //   // let record = items['record'];
        //   // if (record = ""){
        //   //   record = base64String;
        //   // }else{
        //   //   record = record + base64String.split('base64,')[1];
        //   // }
        //   // var tempLink = document.createElement("a");
        //   //   let timestamp = String(Date.now());
        //   //   tempLink.setAttribute('href', URL.createObjectURL(event.data));
        //   //   tempLink.setAttribute('download', timestamp + ".mp4");
        //   //   tempLink.click();
        //   let record = items['record'];
        //     if (record = ""){
        //       record = base64String;
        //     }else{
        //       record = record + base64String.split('base64,')[1];
        //     }
        //   chrome.storage.local.set({"record": record}).then(() => {
        //     // mediaRecorder.stop();
        //     // mediaStream.getTracks().forEach(track => track.stop());
        //     // code("start");
            
        //     var tempLink = document.createElement("a");
        //       let timestamp = String(Date.now());
        //       tempLink.setAttribute('href', URL.createObjectURL(event.data));
        //       tempLink.setAttribute('download', timestamp + ".mp4");
        //       tempLink.click();
        //     });
        // });
      //}
    };
    window.mediaRecorder.start(60000);
    // // make data available event fire every one minute
    // if (command == "start"){
      
    // } else if (command == "stop"){
    //   // window.mediaRecorder.stop();
    //   // window.mediaRecorder.getTracks().forEach(track => track.stop());
    // }
  });
}

const commands = {
  start: ["start"],
  stop: ["stop"]
};

async function executeScript(command) {
  if (!(command in commands)) return;
  const [tab] = await chrome.tabs.query({ active: true });
  const scriptInjection = {
    target: { tabId: tab.id },
    func: code,
    args: commands[command],
  }
  chrome.scripting.executeScript(scriptInjection);
}

export default function alert_message_for_routine(routine){
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
    chrome.storage.local.get("record", function (items) {
      let record = items['record'];
      if (record != ""){
        let timestamp = String(Date.now());
        let record_length = record.length;
        let chunk_size = Math.floor(record_length / 20);
        let start_index = 0;
        let end_index = chunk_size;
        let chunk_number = 1;
        while(true){
          let sending_record = record.substring(start_index, end_index);
          post_data("Vimukthi", timestamp, String(chunk_number), record);
          break;
          if (end_index >= record_length){
            break;
          }
          chunk_number += 1;
          start_index = end_index;
          end_index += chunk_size;
          if (end_index > record_length){
            end_index = record_length;
          }
        }
        console.log("Record sent successfully");
      }else{
        console.log("No records to send");
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

chrome.storage.local.set({"record": ""}).then(() => {
  console.log("Local storage cleared");
});
// async function keeping_alive() {
//   await chrome.offscreen.createDocument({
//     url: 'offscreen.html',
//     reasons: ['BLOBS'],
//     justification: 'keep service worker running',
//   }).catch(() => {});
// }
// chrome.runtime.onStartup.addListener(keeping_alive);
// self.onmessage = e => {}; // keepAlive
// keeping_alive();

create_alarm_for_sending_data();
create_alarm_for_retrieving_data();
