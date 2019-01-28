#!/usr/bin/python

from internetarchive.session import ArchiveSession
from internetarchive.search import Search
from internetarchive import download
from moviepy.editor import *
from PIL import Image, ImageOps
import random, os, time

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
downloadNum = randomNum(7,9)
identList = []
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
os.remove("baseVideo.mp4")

#os.system('youtube-upload --title="'+ filename +'" --description="A.S. Mutter plays Beethoven" --category=Music --tags="mutter, beethoven" --recording-date="'+ datenow +'" --default-language="en" --default-audio-language="en"  --client-secrets=client_secrets.json --credentials-file=credentials.json --playlist="Pattern Recog" --file="' + filename + '.mp4"')
