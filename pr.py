#!/usr/bin/python

from internetarchive.session import ArchiveSession
from internetarchive.search import Search
from internetarchive import download
from moviepy.editor import *
from PIL import Image, ImageOps
import random, os, time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import json

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'relative/path/to/file/you/want')

def randomNum(min, max):
    return random.randint(min,max-1)

s = ArchiveSession()
search = Search(s, '(collection:ephemera)')
print("Searching Archive.org for movies")
totalRecords = search.num_found
print("Returned " + str(totalRecords) + " results")
resultList = list(search)
downloadNum = randomNum(6,10)
identList = []
titlename = ""
print("Downloading " + str(downloadNum) + " videos")
for x in range(downloadNum):
    randomRecordNum = randomNum(0,totalRecords)
    randomRecordIndent = resultList[randomRecordNum]['identifier']
    identList.append(randomRecordIndent)
    print("Downloading video " + str(x + 1) + " of " + str(downloadNum))
    download(randomRecordIndent, verbose=True, glob_pattern="*.mp4")
print("Downloaded all video files")
clipList = []
for root, dirs, files in os.walk("./"):
    for file in files:
        if file.endswith(".mp4"):
            filestring = os.path.splitext(file)[0]
            filestringarray = filestring.split()
            if titlename == "":
                titlename = titlename + filestringarray[0] + " "
                print("Generating title: " + titlename)
            clip = VideoFileClip(os.path.join(root, file))
            length = int(clip.duration)
            start = randomNum(0,length-10)
            endCheck = length + 1
            while length < endCheck:
                endCalc = randomNum(9,25)
                endCheck = start + endCalc
            end = randomNum(start+1,start+endCalc)
            cut = clip.subclip(start,end)
            clipList.append(cut)
finalClip = concatenate_videoclips(clipList)
finalClip.resize((1920,1080)).write_videofile("baseVideo.mp4")
search = Search(s, '(mediatype:audio collection:freemusicarchive)')
print("Searching Archive.org for audio")
totalRecords = search.num_found
print("Returned " + str(totalRecords) + " results")
resultList = list(search)
print("Downloading audio")
randomRecordNum = randomNum(0,totalRecords)
randomRecordIndent = resultList[randomRecordNum]['identifier']
print("Downloading")
download(randomRecordIndent, verbose=True, glob_pattern="*.mp3")
musicList = []
for root, dirs, files in os.walk("./"):
    for file in files:
        if file.endswith(".mp3"):
            music = AudioFileClip(os.path.join(root, file))
            musicList.append(music)
print("Mixing audio")
videoclip = VideoFileClip("baseVideo.mp4")
audiotrack = musicList[randomNum(0,len(musicList))]
audioclip = CompositeAudioClip([videoclip.audio.fx(afx.volumex, 1.5), audiotrack.fx(afx.volumex, 0.6)])
videoclip.audio = audioclip
timestamp = str(int(time.time()))
filename = "Pattern_Recog"+timestamp
videoclip.set_duration(videoclip.duration).write_videofile(filename+".mp4")
print("Creating thumbnail")
videoclip.save_frame(filename+".png")
thumb = Image.open(filename+".png")
colors = thumb.getcolors(thumb.size[0]*thumb.size[1])
if colors[len(colors)-1][1] == (0, 0, 0) or colors[len(colors)-1][1] == (11, 11, 11):
    print("Resizing base thumbnail image.")
    thumb = ImageOps.fit(thumb, (2560, 1080), Image.ANTIALIAS, 0, (0.5, 0))
    thumb = thumb.crop((320, 0, 2240, 1080))
new_color = colors[round(len(colors)/7)][1]
foreground = Image.open("logo.png").convert("RGBA")
width, height = foreground.size
for x in range(width):
   for y in range(height):
       current_color = foreground.getpixel((x,y))
       if current_color == (0, 0, 0, 255):
           foreground.putpixel((x,y), new_color)
thumb.paste(foreground, (0, 0), foreground)
thumb.save(filename+".png", format="png")
mainVideo = VideoFileClip(filename+".mp4")
newAudio = mainVideo.audio
newAudio.write_audiofile(filename+".mp3")

### Deep AI text generation ###

API_KEY = 'your_api_key_here'
API_ENDPOINT = 'https://api.deepai.org/api/text-generator'
text_prompt = titlename

# Number of tokens to generate
num_tokens = 100

# Create headers with API key
headers = {
    'api-key': 'deepai text generator key'
}

# Create payload with text prompt and token count
payload = {
    'text': text_prompt,
    'num_tokens': num_tokens
}

# Make POST request to the API
response = requests.post(API_ENDPOINT, headers=headers, data=payload)

data = response.json()
generated_text = data['output']
print(generated_text)


### YouTube upload ###
print("Starting YouTube upload")

# Set your OAuth 2.0 credentials JSON file (downloaded from Google Cloud Console)
CLIENT_SECRETS_FILE = "client_secrets.json"

# Set the video file path
VIDEO_FILE = filename+".mp4"

# Set the YouTube API version
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Set scopes for OAuth
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Authenticate and authorize the user
#flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #CLIENT_SECRETS_FILE, SCOPES)
#credentials = flow.run_local_server(port=0)

# Create a YouTube Data API client instance
#youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# Upload the video
#request = youtube.videos().insert(
 #   part="snippet,status",
 #   body={
 #       "snippet": {
  #          "title": titlename + "| Office For Sleepcore",
  #          "description": generated_text,
  #          "tags": ["sleepcore", "ambient", "documentary", "clips"],
   #         "categoryId": "22"
   #     },
  #      "status": {
 #           "privacyStatus": "public"  # Privacy status: private, unlisted, or public
   #     }
 #   },
 #   media_body=VIDEO_FILE
#)

#response = request.execute()

#print("Video uploaded: https://www.youtube.com/watch?v=" + response['id'])

os.remove("baseVideo.mp4")
