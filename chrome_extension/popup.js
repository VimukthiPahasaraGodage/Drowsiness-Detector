const buttons = Array.from(document.querySelectorAll("button"));

chrome.runtime.onMessage.addListener(({command}) => {
  alert_message(command);
});

function alert_message(command){
  alert(command);
}

buttons.forEach(button => button.onclick = () => {
  const command = button.dataset.command;
  chrome.runtime.sendMessage({ command });
});