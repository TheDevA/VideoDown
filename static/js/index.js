const sendButton = document.querySelector("#sendBtn")
const linkInp = document.querySelector("#linkInp")

// function for handling style of the video url input and checking the value of url
function sendingUrl() {
  let url = linkInp.value
  if (url != "") {
    linkInp.placeholder = "Please type the url for the video" 
    linkInp.style.borderColor = "rgba(255,209,0, 0.8)"
    linkInp.style.boxShadow = "0 1px 1px rgba(0, 0, 0, 0.075) inset, 0 0 8px rgba(255,209,0, 0.6)"
    linkInp.style.outline = "0 none"
    window.location.href = "video?url="+url
  }else{
    linkInp.style.borderColor = "rgba(255,0,0, 0.8)"
    linkInp.style.boxShadow = "0 1px 1px rgba(0, 0, 0, 0.075) inset, 0 0 8px rgba(255,0,0, 0.6)"
    linkInp.style.outline = "0 none"
    linkInp.placeholder = "URL is required"
  }
}

sendButton.addEventListener("click",sendingUrl)