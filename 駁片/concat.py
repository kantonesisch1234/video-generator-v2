from moviepy.editor import *
from os import listdir, mkdir
from os.path import isfile, join, exists, basename
from math import ceil
import winsound

mindur = 60

dir = r'.\videos'
output_dir = join(dir, 'concatenated')
if not exists(output_dir):
    mkdir(output_dir)
    
files = [join(dir,f) for f in listdir(dir) if isfile(join(dir, f)) and f.endswith('.mp4')]

for video in files:
    filename = basename(video)
    clip = VideoFileClip(video)
    dur = clip.duration
    if dur < mindur:
        no_to_concatenate = ceil(mindur/dur)
        clips = concatenate_videoclips([clip]*no_to_concatenate)
        clips.write_videofile(join(output_dir, filename))

winsound.Beep(int(1000), int(5000))