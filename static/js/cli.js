// selecting cpanel dom elemnts
const textaLogs = document.querySelector("#floatingTextarea2")
const textaRealTime = document.querySelector("#floatingTextarea1")
const linkInp = document.querySelector("#linkInp")
const enterBtn = document.querySelector(".enterBtn")

// socket setup
let socket = io();

socket.on("connect",()=>{  
  socket.emit("sendLogs",{})
})


// socket handler for filling info of the logs
socket.on("logs",(data)=>{
  textaLogs.value = ""
  logs = data["logs"]

  for (let index = 0; index < logs.length; index++) {
    
    textaLogs.value = textaLogs.value +"|  "+(index + 1 )+"  | "+ logs[index]
    
  }
  
})

// sending the command to backend
enterBtn.addEventListener('click',()=>{
  if (linkInp.value == "clear") { 
    textaRealTime.value = ""
  }else if (linkInp.value != ""){
    socket.emit("command",{"cmd":linkInp.value})
    textaRealTime.value = textaRealTime.value + "(+) Running: "+ linkInp.value + "\n"
  }
})

// socket handler for filling command output in realtime
socket.on("cmdOutput",(data)=>{
  if (data["output"] !="") {
    textaRealTime.value = textaRealTime.value + data["output"]
    textaLogs.scrollTop = textaLogs.scrollHeight
    textaRealTime.scrollTop = textaRealTime.scrollHeight
  }else{
    textaRealTime.value = textaRealTime.value + data["oErorr"]
    textaLogs.scrollTop = textaLogs.scrollHeight
    textaRealTime.scrollTop = textaRealTime.scrollHeight
  }
  socket.emit("sendLogs",{})
  
})