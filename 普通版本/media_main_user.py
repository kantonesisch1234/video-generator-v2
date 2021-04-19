from text_preprocessing import *
from make_media import *
from math import ceil, floor
import os
import winsound

fps = 30

# Alarm
duration = 3000  # milliseconds
freq = 920  # Hz

narration_lang = "zh-tw"

video_size_list = [(192,144), (426, 240), (640, 360), (852, 480), (1280, 720), (1920, 1080)]

print("選擇影片質素：")
print("1. 144p")
print("2. 240p")
print("3. 360p")
print("4. 480p")
print("5. 720p")
print("6. 1080p")
video_size_choice = input("輸入數字(1-6)： ")
video_size = video_size_list[int(video_size_choice)-1]

print("\n隨機剪片選擇：")
print("1. 依次序")
print("2. 隨機")
random_par = input("輸入選擇(1或2)")
if random_par == '1':
    shuffle = False
    random_timeframe = False
if random_par == '2':
    shuffle = True
    random_timeframe = True

random_split_video_into_str = input("\n 每段片拆成幾多段？ (輸入整數)： ")
random_split_videos_into = int(random_split_video_into_str)

subtitles_font_size = 64*video_size[1]/1080
subtitles_font = 'DFKai-SB'
subtitles_bar_thickness = 2
words_per_line = 26

subtitles_bar_size = (4000,ceil(subtitles_font_size*4/3)*subtitles_bar_thickness)

is_bgm_str = input("\n是否需要背景音樂？(是則輸入y，否則輸入n): ")
is_bgm = bool(is_bgm_str)
bgm_vol = 0.30

print("\n背景音樂：")
bgm_list = []
for file in os.listdir(bgm_dir):
    if file.endswith('.mp3'):
	    bgm_list.append(file)

for idx,file in enumerate(bgm_list):
    print(idx+1, ": ", file)
bgm_idx = input("輸入背景音樂號碼：")

bgm_file = bgm_list[int(bgm_idx)-1]

logo_size = (200*video_size[1]/1080, 200*video_size[1]/1080)
logo_opacity = 0.3

print('\n')
if __name__ == '__main__':
    sentences = get_subtitles_from_textfile('text.txt', lang=narration_lang, words_per_line=words_per_line)
    subtitles = generate_audio_files(sentences, lang=narration_lang)
    narration = AudioFileClip(os.path.join(output_dir,'text.mp3'))
    duration = narration.duration
    input_clip = make_clip_from_directory(media_source_dir, output_dir,duration,size=video_size,subtitles_bar_size=subtitles_bar_size, shuffle=shuffle, random_timeframe=random_timeframe, random_split_videos_into=random_split_videos_into, logo_size=logo_size, logo_opacity = logo_opacity, fps=fps)
    insert_audio_and_subtitles(input_clip,'output.mp4','text.mp3',subtitles,fontsize=subtitles_font_size,
    font=subtitles_font, is_bgm=is_bgm, bgm_vol=bgm_vol, bgm_file=bgm_file)
    winsound.Beep(int(freq), int(duration))