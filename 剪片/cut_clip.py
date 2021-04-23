from moviepy.editor import *
import os

def get_sec(time_str):
    if time_str.count(':') == 1:
        m, s = time_str.split(':')
        return int(m) * 60 + float(s)
    elif time_str.count(':') == 2:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)

folder = r'.\原片'
output_folder = r'.\輸出'
filename = os.listdir(folder)[0]
output_filename = os.path.join(output_folder, filename)
file = os.path.join(folder,filename)
start_str = input("輸入片段開始時間：")
end_str = input("輸入片段結束時間：")
start_time, end_time = get_sec(start_str), get_sec(end_str)

VideoFileClip(file).subclip(start_time,end_time).write_videofile(output_filename)
