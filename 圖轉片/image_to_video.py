from moviepy.editor import *
import os

img_dir = r'.\圖'
video_dir = r'.\片'

img_duration = float(input('輸入影片長度：'))

imgfiles = os.listdir(img_dir)
filenames = [os.path.splitext(imgfile)[0] for imgfile in imgfiles]

for idx,imgfile in enumerate(imgfiles):
    clip = ImageClip(os.path.join(img_dir,imgfile), duration=img_duration)
    clip.write_videofile(os.path.join(video_dir,filenames[idx]+'.mp4'), fps = 30)