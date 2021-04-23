from text_preprocessing import *
from moviepy.editor import *

if __name__ == '__main__':
    video = ColorClip((50,50), duration=700,color=[0,0,0])
    video.audio = AudioFileClip('text.mp3')
    video.write_videofile('output.mp4',fps=10)