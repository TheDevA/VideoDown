from flask import Flask, render_template, url_for, request,redirect,send_from_directory
import yt_dlp
from yt_dlp.utils import DownloadError
from flask_socketio import SocketIO, emit
import os,threading,subprocess

from engineio.payload import Payload

Payload.max_decode_packets = 1000

app = Flask(__name__)
socketio = SocketIO(app,async_mode="threading")

# function for loging
def writingToLog(info):
  with open('logs.txt', 'a') as f:
    f.write(info)
    f.close()
# function for getting video info
def main(URL, ORDER):
  if ORDER == "INFO":
    formats = []
    title = ""
    id = ""
    duration = ""
    uploader = ""
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
      try:
        info0 = ydl.extract_info(URL, download=False)
      except DownloadError as e:
        DATA = {"ERROR": str(e.msg)}
        return DATA
      title = info0['title']
      id = info0["id"]
      thumbnail = info0["thumbnail"]
      duration = info0["duration"]
      uploader = info0["uploader"]
      formats = info0["formats"]
    DATA = {
      "ERROR": 0,
      "title": title,
      "id": id,
      "channel": uploader,
      "thumbnail": thumbnail,
      "duration": round(duration / 60, 2),
      "formats": formats
    }
    return DATA


# function for post proccising hook
def myPHook(d):
  fileStatus = d["status"]
  if fileStatus == "started":
    with app.test_request_context('/'):
      socketio.emit("pprog",{
        "status":fileStatus,
        "postprocessor":d["postprocessor"]
      })
  elif fileStatus == "finished":
    with app.test_request_context('/'):
      socketio.emit("pprog",{
        "status":fileStatus,
        "postprocessor":d["postprocessor"]
      })
  elif fileStatus == "processing":
    with app.test_request_context('/'):
      socketio.emit("pprog",{
        "status":fileStatus,
        "postprocessor":d["postprocessor"]
      })

# function for downloading hook
def myHook(d):
  fileStatus = d["status"]
  
  if fileStatus == "finished":
    with app.test_request_context('/'):
      socketio.emit("prog",{
        "downloaded_bytes": d["downloaded_bytes"],
        "status":fileStatus,
        "filename":d["filename"],
        "total_bytes":d["total_bytes"]
      })
  elif fileStatus == "error":
    with app.test_request_context('/'):
      socketio.emit("prog",{
        "status":fileStatus,
        "filename":d["filename"],
        "total_bytes":d["total_bytes"]
      })
  elif fileStatus == "downloading":
    with app.test_request_context('/'):
      socketio.emit("prog",{
        "downloaded_bytes": d["downloaded_bytes"],
        "speed":d["speed"],
        "status":fileStatus,
        "filename":d["filename"],
        "total_bytes":d["total_bytes_estimate"]
        
      })


# function for downloading the video with the format and ext choosed
def downloading(url, format, ext):
  baseFormats = ["b", "bv", "ba", "bv*", "ba*"]
  if baseFormats.count(format) > 0:
    if ext == "mp3":
      ydlOps = {
        "quiet": True,
        'progress_hooks': [myHook],
        "postprocessor_hooks":[myPHook],
        'final_ext': 'mp3',
        "ffmpeg_location": "./ffmpegFolder",
        "outtmpl" : "./downloads/%(title)s-%(uploader)s.%(ext)s",
        "format": format,
        'postprocessors': [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
      }
    else:
      ydlOps = {
        "quiet": True,
        'progress_hooks': [myHook],
        "postprocessor_hooks":[myPHook],
        "merge_output_format": "mp4",
        'final_ext': 'mp4',
        "ffmpeg_location": "./ffmpegFolder",
        "outtmpl": "./downloads/%(title)s-%(uploader)s.%(ext)s",
        "format": format,
      }
  else:
    if ext == "mp3":
      ydlOps = {
        "quiet": True,
        "postprocessor_hooks":[myPHook],
        'progress_hooks': [myHook],
        'final_ext': 'mp3',
        "ffmpeg_location": "./ffmpegFolder",
        "outtmpl" : "./downloads/%(title)s-%(uploader)s.%(ext)s",
        "format": format,
        'postprocessors': [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
      }
    else:
      ydlOps = {
        "quiet": True,
        "postprocessor_hooks":[myPHook],
        'progress_hooks': [myHook],
        "merge_output_format": "mp4",
        'final_ext': 'mp4',
        "ffmpeg_location": "./ffmpegFolder",
        "outtmpl": "./downloads/%(title)s-%(uploader)s.%(ext)s",
        "format": format + "+ba",
      }
  with yt_dlp.YoutubeDL(ydlOps) as ydl:
    URL = [url]
    try:
      ydl.download(URL)
    except DownloadError as e:
      writingToLog(e.msg)



# main page rout
@app.route('/')
def index():
  return render_template("index.html")

# video info route
@app.route("/video")
def video():
  url = request.args.get("url")
  if url != None:
    return render_template("video.html")
  else:
    return "<h1>Need URL</h1>"

# hidden route for downloading
@app.route("/download")
def download():
  url = request.args.get("url")
  format = request.args.get("format")
  ext = request.args.get("ext")
  if url != None and ext != None and format != None:
    downloadingThread= threading.Thread(target=downloading,args=(url,format,ext))
    downloadingThread.start()
    return redirect(url_for("fS"))
  else:
    return "<h1>Missing Info</h1>"

# file system route
@app.route("/fileSystem")
def fS():
   return render_template("download.html")

# hidden route for downloading files from file system
@app.route('/fileSystem/downloads/<path:filename>', methods=['GET', 'POST'])
def downloads(filename):
    uploads = os.getcwd() + "/downloads"
    return send_from_directory(directory=uploads, path=filename)

# cpanel route
@app.route("/cli")
def cli():
  return render_template("cli.html")




# socket handler for the video url and sending the video info
@socketio.on('url')
def handle_message(data):
  url = data['url']
  if url != 0:
    DATA = main(url, "INFO")
    emit("DATA", DATA)
  else:
    print("NO URL")




# socket handler for sending files in file system
@socketio.on("NeedData")
def handle_fileSysytem(d):
  path = os.getcwd() + "/downloads"

  downloadedFilesList = os.listdir(path)
  downloadedFiles = []
  for file in downloadedFilesList:
    fileSize = os.stat(path+"/"+file)
    downloadedFilesDict = {"fileName":file,"fileSizeB":fileSize.st_size}
    downloadedFiles.append(downloadedFilesDict)
  emit("downloadedFiles",{"files":downloadedFiles})


# socket handler for sending log data
@socketio.on("sendLogs")
def handle_logs(x):
  with open('logs.txt') as f:
    lines = f.readlines()
    emit("logs",{"logs":lines})






# socket handler for the cpanle command and sending the output
@socketio.on("command")
def handling_command(command):
  cmd = command["cmd"]
  with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0,shell=True,stderr=subprocess.PIPE
) as p:
    char = p.stdout.read(1)
    chare = p.stderr.read(1)
    while char != b'' or  chare!= b'':

        if char != b'':
          writingToLog(char.decode("UTF-8"))
        else:
          writingToLog(chare.decode("UTF-8"))
        emit("cmdOutput",{"output":char.decode('UTF-8'),"oErorr":chare.decode("UTF-8")})
        char = p.stdout.read(1)
        chare = p.stderr.read(1)
        

# running the app
socketio.run(app, host='0.0.0.0', port=81, debug=False,allow_unsafe_werkzeug=True)

